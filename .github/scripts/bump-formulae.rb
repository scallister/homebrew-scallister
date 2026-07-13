#!/usr/bin/env ruby
# frozen_string_literal: true

require "json"
require "net/http"
require "rubygems"
require "uri"

FORMULA_DIR = File.expand_path("../../Formula", __dir__)
AUTOBUMP_PATTERN = /#\s*autobump:\s*([^\s#]+)/i
VERSION_PATTERN = /^\s*version\s+"([^"]+)"/m
TAG_PATTERN = /^\s*tag:\s*"([^"]+)"/m
BRANCH_PATTERN = /^\s*branch:\s*"([^"]+)"/m

def github_token
  ENV.fetch("GITHUB_TOKEN", nil)
end

def github_get(path)
  uri = URI("https://api.github.com#{path}")
  http = Net::HTTP.new(uri.host, uri.port)
  http.use_ssl = true

  request = Net::HTTP::Get.new(uri)
  request["Accept"] = "application/vnd.github+json"
  request["User-Agent"] = "homebrew-scallister-bump-formulae"
  request["Authorization"] = "Bearer #{github_token}" if github_token

  response = http.request(request)
  unless response.is_a?(Net::HTTPSuccess)
    abort "GitHub API error for #{path}: #{response.code} #{response.body}"
  end

  JSON.parse(response.body)
end

def fetch_release_tags(owner, repo)
  tags = []
  page = 1

  loop do
    batch = github_get("/repos/#{owner}/#{repo}/tags?per_page=100&page=#{page}")
    break if batch.empty?

    tags.concat(batch.map { |tag| tag["name"] }.grep(/\Av\d/i))
    break if batch.length < 100

    page += 1
  end

  tags
end

def semver_key(tag)
  Gem::Version.new(tag.sub(/\Av/i, ""))
rescue ArgumentError
  nil
end

def latest_release_tag(tags)
  tags
    .map { |tag| [tag, semver_key(tag)] }
    .reject { |(_, version)| version.nil? }
    .max_by { |(_, version)| version }
    &.first
end

def parse_autobump_repo(contents)
  match = contents.match(AUTOBUMP_PATTERN)
  return nil unless match

  repo = match[1]
  abort "Invalid autobump repo #{repo.inspect}" unless repo.include?("/")

  owner, name = repo.split("/", 2)
  [owner, name]
end

def current_version(contents)
  match = contents.match(VERSION_PATTERN)
  match&.[](1)
end

def version_outdated?(current, latest)
  current_version = semver_key(current)
  latest_version = semver_key(latest)
  return true if current_version.nil? || latest_version.nil?

  latest_version > current_version
end

def bump_formula_contents(contents, new_tag)
  updated = contents.gsub(VERSION_PATTERN, %(  version "#{new_tag}"))

  if updated.match?(TAG_PATTERN)
    updated = updated.gsub(TAG_PATTERN, %(    tag: "#{new_tag}",))
  elsif updated.match?(BRANCH_PATTERN)
    updated = updated.gsub(BRANCH_PATTERN, %(    tag: "#{new_tag}",))
  else
    abort "Formula is missing tag: or branch: in url block"
  end

  updated
end

def process_formula(path, dry_run:)
  contents = File.read(path)
  repo_parts = parse_autobump_repo(contents)
  return :skipped unless repo_parts

  owner, repo = repo_parts
  formula_version = current_version(contents)
  abort "#{path}: missing version line" if formula_version.nil?

  latest_tag = latest_release_tag(fetch_release_tags(owner, repo))
  if latest_tag.nil?
    warn "#{path}: no v* release tags found for #{owner}/#{repo}"
    return :skipped
  end

  if formula_version == latest_tag
    puts "#{path}: up to date (#{latest_tag})"
    return :current
  end

  unless version_outdated?(formula_version, latest_tag)
    puts "#{path}: formula version #{formula_version} is newer than latest tag #{latest_tag}, skipping"
    return :skipped
  end

  puts "#{path}: #{formula_version} -> #{latest_tag}"
  unless dry_run
    File.write(path, bump_formula_contents(contents, latest_tag))
  end

  :bumped
end

dry_run = ARGV.include?("--dry-run")
checked = 0
bumped = 0
current = 0
skipped = 0

Dir.glob(File.join(FORMULA_DIR, "*.rb")).sort.each do |path|
  next unless File.file?(path)

  checked += 1
  case process_formula(path, dry_run: dry_run)
  when :bumped then bumped += 1
  when :current then current += 1
  when :skipped then skipped += 1
  end
end

puts "Checked #{checked} formulae: bumped #{bumped}, current #{current}, skipped #{skipped}"
