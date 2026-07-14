# autobump: scallister/wemowatch
class Wemowatch < Formula
  desc "Wemowatch"
  homepage "https://github.com/scallister/wemowatch"
  url "https://github.com/scallister/wemowatch.git",
    tag: "v1.0.5",,
    :using => :git
  version "v1.0.5"

  depends_on "go" => :build

  def install
    system "go", "build", *std_go_args
  end
end
