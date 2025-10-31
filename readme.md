# AI-Yashvi - JainQuest 🙏

## Spiritual Guide for Jain Philosophy and Daily Practice

AI-Yashvi (JainQuest) is an intelligent Streamlit-based chatbot application designed to provide authentic spiritual guidance rooted in Jain philosophy. The application combines AI-powered conversational capabilities with a comprehensive knowledge base to help users explore Jain teachings, practices, and principles.

---

## 🌟 Core Features

### 1. **AI-Powered Chat Interface**
- Interactive conversational AI for answering spiritual questions
- Multi-language support (English and Gujarati)
- Context-aware responses based on authentic Jain sources
- Fallback hierarchy using multiple AI models (Bytez SDK, Hugging Face)

### 2. **Quick Questions Database**
- Pre-written answers to common Jain topics
- Instant access to fundamental concepts like:
  - Navkar Mantra
  - Ahimsa (Non-violence)
  - Three Jewels of Jainism
  - Karma Theory
  - Ayambil and spiritual fasting
  - Meditation techniques
  - Vegetarianism in Jainism

### 3. **Learning Resources**
- Curated collection of authentic Jain knowledge sources
- Featured content from Digital Jain Pathshala
- Links to trusted resources including:
  - Jain eLibrary
  - JainQQ
  - JainWorld
  - Jainpedia
  - And more

### 4. **Content Safety & Guidelines**
- Built-in content moderation for prohibited topics
- Aligned responses with Jain principles
- Appropriate spiritual guidance and redirections

### 5. **User Management**
- Daily question limits (configurable)
- Admin mode for unlimited access
- User profiles and personalization
- Session management with conversation history

### 6. **Knowledge Base Integration**
- Automatic GitHub repository content loading
- Document search and retrieval
- Context-aware answer generation
- Support for multiple file formats (.txt, .md, .py, .json, .yaml)

---

## 🚀 Getting Started

### Prerequisites

Before running the application, ensure you have:
- Python 3.8 or higher
- pip (Python package installer)
- Git (for repository cloning)

### Installation

1. **Clone the repository:**
```bash
git clone https://github.com/saumyasanghvi03/AI-Yashvi.git
cd AI-Yashvi
```

2. **Install required dependencies:**
```bash
pip install streamlit
pip install bytez
pip install transformers torch accelerate
pip install GitPython
pip install pytz
```

Or install all dependencies at once:
```bash
pip install streamlit bytez transformers torch accelerate GitPython pytz
```

3. **Run the application:**
```bash
streamlit run app.py
```

4. **Access the application:**
   - The app will automatically open in your browser
   - Default URL: `http://localhost:8501`

---
## 📖 Usage Guide

### Chat Interface

1. **Navigate to the Chat section** (default landing page)
2. **Type your question** in English or Gujarati
3. **Examples:**
   - "What is the meaning of life according to Jainism?"
   - "How can I practice Ahimsa in daily life?"
   - "જૈન ધર્મ મુજબ જીવનનો અર્થ શું છે?"
4. **Click "Send Question"** or press Enter
5. **Receive formatted responses** with:
   - Main concept
   - Key points
   - Jain principles
   - Practical advice
   - Emotional support
   - Summary

### Quick Questions

1. **Navigate to "Quick Questions"** from the sidebar
2. **Browse organized categories:**
   - Mantras & Practices
   - Core Principles
   - Philosophy & Concepts
   - Lifestyle & Diet
3. **Click "Get Answer"** on any question
4. **View instant pre-written responses** based on authentic sources

### Learning Resources

1. **Navigate to "Learn"** section
2. **Explore featured resources:**
   - Digital Jain Pathshala (highlighted)
   - Additional authentic Jain sources
3. **Access key Jain concepts** with brief descriptions
4. **Click links** to visit external resources

### Settings & Admin Mode

1. **Navigate to "Settings"**
2. **View your statistics:**
   - Daily question limit
   - Questions asked today
   - Remaining questions

---

## 🏗️ Technical Architecture

### Core Components

1. **Streamlit UI Framework**
   - Responsive web interface
   - Custom CSS styling
   - Multi-page navigation

2. **AI Model Integration**
   - Primary: Bytez SDK (Qwen/Gemma models)
   - Fallback: Hugging Face Transformers (DialoGPT/DistilGPT2)
   - Caching mechanism for performance

3. **Knowledge Base**
   - GitHub repository cloning
   - Document parsing and indexing
   - Keyword-based search
   - Context extraction

4. **Session Management**
   - Conversation history (last 6 messages)
   - User state persistence
   - Daily limit tracking with IST timezone
   - Admin mode authentication

5. **Content Processing**
   - Language detection (English/Gujarati)
   - Sensitive topic filtering
   - Response formatting (bullet points)
   - Context augmentation

### Key Functions

- `cached_initialize_ai_models()`: Loads AI models with caching
- `cached_load_repo_content()`: Loads knowledge base from GitHub
- `get_ai_response()`: Main function for generating responses
- `search_in_repo()`: Searches documents for relevant context
- `detect_language()`: Identifies user's language
- `detect_sensitive_topic()`: Content moderation
- `render_*_page()`: UI rendering functions

---

## 🔒 Security & Privacy

- **Content Moderation**: Built-in filtering for inappropriate topics
- **Rate Limiting**: Daily question limits to prevent abuse
- **Admin Authentication**: Password-protected admin features
- **No Data Storage**: Conversations are session-based only
- **Feedback Logging**: Optional feedback saved locally (feedback.txt)

---

## 🌐 Supported Languages

- **English**: Full support for questions and responses
- **Gujarati**: Full support for questions and responses
- **Bilingual Headers**: All responses include both English and Gujarati section headers

---

## 📚 Knowledge Sources

The application integrates content from:

1. **Digital Jain Pathshala** (Featured)
   - Blogs and spiritual guides
   - Ayambil and fasting practices
   - Navpad Oli information
   - Meditation techniques

2. **Additional Sources:**
   - Jain eLibrary
   - JainQQ
   - JainWorld
   - HereNow4U
   - Jainpedia
   - Jain Philosophy
   - Jain Study
   - Jain Heritage
   - Jain Scriptures
   - Jain Meditation

---

## 🛠️ Troubleshooting

### Common Issues

**Issue 1: AI models not loading**
- **Solution**: Ensure `bytez` and `transformers` packages are installed
- **Command**: `pip install bytez transformers torch accelerate`

**Issue 2: Knowledge base loading fails**
- **Solution**: Check internet connection and GitHub repository access
- **Note**: Repository content is cached after first load

**Issue 3: Daily limit reached**
- **Solution**: Wait until midnight IST for automatic reset
- **Alternative**: Use admin mode (requires password)

**Issue 4: Bytez API errors**
- **Solution**: Verify API key is valid
- **Fallback**: App will automatically use Hugging Face models

---

## 🤝 Contributing

We welcome contributions to improve AI-Yashvi! Here's how you can help:

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Make your changes**
4. **Commit with clear messages**
   ```bash
   git commit -m "Add: Description of your changes"
   ```
5. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```
6. **Create a Pull Request**

### Areas for Contribution

- Additional Jain knowledge content
- UI/UX improvements
- New language support
- Bug fixes and optimizations
- Documentation enhancements

---

## 📝 License

This project is part of the Jain community's effort to make spiritual knowledge accessible. Please use responsibly and maintain the authenticity of Jain teachings.

---

## 📞 Contact & Support

- **Repository**: [https://github.com/saumyasanghvi03/AI-Yashvi](https://github.com/saumyasanghvi03/AI-Yashvi)
- **Issues**: Report bugs or request features via GitHub Issues
- **Feedback**: Use the in-app feedback form (Settings section)

---

## 🙏 Acknowledgments

- **Digital Jain Pathshala** for providing comprehensive spiritual content
- **Jain Community** for authentic source materials
- **Bytez** for AI model infrastructure
- **Streamlit** for the web framework
- **Hugging Face** for transformer models

---

## 📊 Version Information

- **Current Version**: 1.0
- **Last Updated**: October 31, 2025
- **Python Version**: 3.8+
- **Streamlit Version**: Latest stable

---

## 🎯 Future Roadmap

- [ ] Voice input/output capabilities
- [ ] Mobile app version
- [ ] Expanded language support (Hindi, Sanskrit)
- [ ] Advanced meditation timers
- [ ] Community discussion forums
- [ ] Daily spiritual practice reminders
- [ ] Personalized learning paths

---

## ⚠️ Disclaimer

This AI assistant provides general spiritual guidance based on Jain philosophy. For specific religious questions, complex spiritual matters, or personal guidance, please consult qualified Jain scholars or spiritual teachers. The application is meant to supplement, not replace, traditional learning and mentorship.

---

**Made with ❤️ for the Jain Community**

*Jai Jinendra* 🙏
