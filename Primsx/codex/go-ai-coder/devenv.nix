{ pkgs, ... }:

{
  packages = [ 
    pkgs.go_1_24
    pkgs.ripgrep
    pkgs.git
  ];

  env = {
    # Set Go version
    GOROOT = "${pkgs.go_1_24}/share/go";
    PATH = "${pkgs.go_1_24}/bin:${pkgs.ripgrep}/bin:${pkgs.git}/bin:$PATH";
  };

  enterShell = ''
    echo "🚀 Coding Agent Workshop Environment"
    echo "Go version: $(go version)"
    echo "Ripgrep version: $(rg --version | head -1)"
    echo ""
    echo "Next steps:"
    echo "1. Copy env.example to .env and add your AIMLAPI API key"
    echo "2. Run: go mod tidy"
    echo "3. Start with: go run chat.go"
  '';
}
