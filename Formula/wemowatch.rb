class Wemowatch < Formula
  desc "Wemowatch"
  homepage "https://github.com/scallister/wemowatch"
  url "https://github.com/scallister/wemowatch.git",
    branch: "master",
    :using => :git

  version "v1.0.2"

  depends_on "go" => :build

  def install
    system "go", "build", *std_go_args
  end
end

