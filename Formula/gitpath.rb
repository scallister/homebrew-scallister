class Gitpath < Formula
  desc "Tool to generate GitHub and GitLab urls from paths"
  homepage "https://github.com/scallister/gitpath"
  url "https://github.com/scallister/gitpath.git",
    branch: "main",
    :using => :git

  version "v0.0.2"

  depends_on "go" => :build

  def install
    system "go", "build", *std_go_args
  end
end

