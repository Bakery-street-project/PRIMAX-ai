# ☁️ CloudyMcCodeFace - Enterprise AI Coding Assistant

[![Go Version](https://img.shields.io/badge/Go-1.21+-blue.svg)](https://golang.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![AI Powered](https://img.shields.io/badge/AI-Powered-purple.svg)](https://ollama.ai)
[![GitHub Stars](https://img.shields.io/github/stars/booze/CloudyMcCodeFace.svg)](https://github.com/booze/CloudyMcCodeFace)

> **The Ultimate AI-Powered Coding Assistant for Go Developers**

CloudyMcCodeFace is a sophisticated, enterprise-grade AI coding assistant that combines the power of local AI models with GitHub integration, web scraping, and intelligent code analysis. Built with Go and powered by Ollama, it provides a secure, private, and highly customizable coding experience.

## ✨ Features

### 🧠 **AI-Powered Intelligence**
- **Hybrid AI Architecture** - Local Ollama + Cloud AI with smart fallback
- **Go-Specific Models** - Fine-tuned models optimized for Go development
- **Context-Aware Conversations** - Remembers conversation history
- **Intelligent Code Analysis** - Understands and explains your code
- **Learning Mode** - Continuously learns from Go ecosystem
- **Cloud AI Service** - Enterprise-grade cloud deployment ready

### 🔧 **GitHub Integration**
- **Repository Analysis** - Analyze your GitHub repositories
- **Smart Search** - Find relevant repositories and code
- **Issue & PR Analysis** - Get insights on project health
- **Rate Limit Handling** - Graceful fallbacks for API limits

### 🌐 **Web Scraping & Research**
- **Autonomous Learning** - Scrapes and learns from Go resources
- **Topic Research** - Deep dive into specific technologies
- **Content Analysis** - AI-powered insights from web content
- **Curated Resources** - Access to best Go learning materials

### ⚙️ **Enterprise Features**
- **Multi-Cloud Deployment** - AWS, GCP, Azure support
- **Custom Model Training** - Train Go-specific AI models
- **Secure Configuration** - Encrypted settings and session management
- **Command-Line Interface** - Full CLI with flags and options
- **Conversation Persistence** - Auto-save and history management
- **Extensible Architecture** - Plugin-ready design
- **Production Ready** - Complete deployment and monitoring

## 🚀 Quick Start

### Prerequisites

1. **Go 1.21+** - [Install Go](https://golang.org/doc/install)
2. **Ollama** - [Install Ollama](https://ollama.ai/download)
3. **GitHub Token** (optional) - [Create Personal Access Token](https://github.com/settings/tokens)

### Installation

```bash
# Clone the repository
git clone https://github.com/booze/CloudyMcCodeFace.git
cd CloudyMcCodeFace

# Install dependencies
go mod tidy

# Build the application
go build -o cloudy-mc-codeface cmd/main.go

# Install to your PATH (optional)
sudo cp cloudy-mc-codeface /usr/local/bin/
```

### Basic Usage

```bash
# Start with default settings
cloudy-mc-codeface

# Use custom model
cloudy-mc-codeface --model codellama:13b --tokens 4000

# Use cloud AI with fallback
cloudy-mc-codeface --cloud --cloud-url "https://your-service.com" --fallback

# Enable verbose mode
cloudy-mc-codeface --verbose

# Show help
cloudy-mc-codeface --help
```

## ☁️ Cloud AI Deployment

### Quick Cloud Setup

```bash
# Set up cloud environment
export CLOUD_PROVIDER="aws"  # or gcp/azure
export GITHUB_TOKEN="your_token"
./setup-cloud-environment.sh

# Deploy cloud AI service
./deploy-cloud-ai.sh

# Train custom Go model
source go-ai-env/bin/activate
python go-ai-model-trainer.py
```

### Cloud AI Features
- **Hybrid Architecture** - Local + Cloud AI with smart fallback
- **Go-Specific Models** - Fine-tuned for Go development
- **Multi-Cloud Support** - Deploy on AWS, GCP, or Azure
- **Production Ready** - Complete monitoring and scaling
- **Custom Training** - Train models on your Go codebase

For detailed setup instructions, see [CLOUD_AI_SETUP_GUIDE.md](CLOUD_AI_SETUP_GUIDE.md)

## 📖 Documentation

### Configuration

The application supports multiple configuration methods:

#### Environment Variables
```bash
export AI_MODEL="llama3.2:3b"
export AI_MAX_TOKENS="2000"
export AI_TEMPERATURE="0.7"
export OLLAMA_URL="http://localhost:11434/v1"
export GITHUB_TOKEN="your_token_here"
export LEARNING_DIR="ai_learning"
export CACHE_ENABLED="true"
export AUTO_SAVE="true"
export VERBOSE="false"
```

#### Command Line Flags
```bash
cloudy-mc-codeface \
  --model llama3.2:3b \
  --tokens 2000 \
  --temp 0.7 \
  --ollama http://localhost:11434/v1 \
  --learning ai_learning \
  --cache \
  --autosave \
  --verbose
```

### Commands

#### Core Commands
- `help` - Show help message
- `config` - Display current configuration
- `quit` / `exit` - Exit the application

#### File Operations
- `read <file_or_folder>` - Read and analyze file content
- `list <directory>` - List directory contents with analysis

#### GitHub Integration
- `github repos` - List and analyze your repositories
- `github search <query>` - Search GitHub repositories
- `github issues <repo>` - Analyze repository issues
- `github prs <repo>` - Analyze pull requests
- `github clone <repo>` - Clone a repository

#### AI Learning
- `ai learn` - Comprehensive Go ecosystem research
- `ai research <topic>` - Research specific topics
- `ai scrape <url>` - Learn from web content
- `go resources` - Show curated Go learning resources

### Examples

```bash
# Analyze your code
You: read main.go

# Search for Go web frameworks
You: github search golang web framework

# Research machine learning in Go
You: ai research machine learning

# Learn from official Go documentation
You: ai scrape https://golang.org/doc/tutorial/

# Get curated Go resources
You: go resources
```

## 🔒 Security

### Privacy First
- **Local Processing** - All AI processing happens locally
- **No Data Collection** - No personal data is sent to external services
- **Secure Storage** - Encrypted configuration and session data
- **Input Sanitization** - All user input is sanitized and validated

### Security Features
- **Token Masking** - Sensitive tokens are never logged
- **URL Validation** - Web scraping URLs are validated for safety
- **Content Limits** - File size and content length limits
- **Secure Filenames** - Generated filenames prevent path traversal

### Best Practices
1. **Use Environment Variables** for sensitive configuration
2. **Regular Updates** - Keep the application updated
3. **Token Rotation** - Regularly rotate GitHub tokens
4. **Local Network** - Run Ollama on localhost only

## 🏗️ Architecture

### Project Structure
```
CloudyMcCodeFace/
├── cmd/                    # Main application
├── internal/               # Internal packages
│   ├── config/            # Configuration management
│   └── security/          # Security utilities
├── configs/               # Configuration files
├── docs/                  # Documentation
├── scripts/               # Build and utility scripts
├── assets/                # Static assets
└── examples/              # Example configurations
```

### Dependencies
- **[Ollama](https://ollama.ai)** - Local AI model runner
- **[OpenAI Go SDK](https://github.com/openai/openai-go)** - AI client library
- **[GoDotEnv](https://github.com/joho/godotenv)** - Environment variable management

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Setup
```bash
# Fork and clone the repository
git clone https://github.com/your-username/CloudyMcCodeFace.git
cd CloudyMcCodeFace

# Install development dependencies
go mod download

# Run tests
go test ./...

# Build for development
go build -o cloudy-mc-codeface cmd/main.go
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

### Built With
- **[Ollama](https://ollama.ai)** - Amazing local AI model runner
- **[Go](https://golang.org)** - The Go programming language
- **[GitHub API](https://docs.github.com/en/rest)** - GitHub's REST API
- **[OpenAI Go SDK](https://github.com/openai/openai-go)** - Official OpenAI Go client

### Inspired By
- **[GitHub Copilot](https://github.com/features/copilot)** - AI pair programming
- **[Cursor](https://cursor.sh)** - AI-powered code editor
- **[Continue](https://continue.dev)** - Open-source AI coding assistant

### Related Projects
- **[awesome-go](https://github.com/avelino/awesome-go)** - Curated Go packages
- **[golangci-lint](https://github.com/golangci/golangci-lint)** - Go linter
- **[cobra](https://github.com/spf13/cobra)** - CLI framework
- **[viper](https://github.com/spf13/viper)** - Configuration management

## 💰 Monetization

### Premium Features (Coming Soon)
- **Advanced AI Models** - Access to premium models
- **Team Collaboration** - Multi-user support
- **Cloud Sync** - Cross-device synchronization
- **Priority Support** - Dedicated support channel
- **Custom Integrations** - API access and webhooks

### Support the Project
- ⭐ **Star the repository** - Help others discover the project
- 🐛 **Report issues** - Help improve the software
- 💡 **Suggest features** - Share your ideas
- 📢 **Spread the word** - Tell other developers

## 📞 Support

- **Documentation** - [Full Documentation](docs/)
- **Issues** - [GitHub Issues](https://github.com/booze/CloudyMcCodeFace/issues)
- **Discussions** - [GitHub Discussions](https://github.com/booze/CloudyMcCodeFace/discussions)
- **Email** - [Contact Support](mailto:support@cloudymccodeface.dev)

---

**Made with ❤️ by the CloudyMcCodeFace team**

*Empowering developers with AI-driven coding assistance*