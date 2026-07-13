# autobump: scallister/cluster-mux
class ClusterMux < Formula
  desc "Helper script for sshing and controlling several hosts while in a tmux session"
  homepage "https://github.com/scallister/cluster-mux"
  url "https://github.com/scallister/cluster-mux.git",
    tag: "v1.0.0",
    :using => :git

  version "v1.0.0"

  depends_on "tmux"

  def install
    bin.install "cluster-mux"
  end

  test do
    assert_match "Usage:", shell_output("#{bin}/cluster-mux help")
  end
end
