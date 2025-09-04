# 🤖 AI Interview Chatbot
<img width="987" height="807" alt="image" src="https://github.com/user-attachments/assets/30d076a5-a3ee-46bc-83e5-8b077e5fd031" />

A Streamlit-based AI-powered technical interview chatbot that conducts personalized interviews based on candidate profiles. The bot collects candidate information, generates relevant technical questions using a local GGUF model, and saves interview data to Excel.

## ✨ Features

- **Candidate Onboarding**: Collects personal and professional information
- **AI-Generated Questions**: Creates personalized technical questions based on experience and tech stack
- **Interactive Chat Interface**: Conversational interview experience
- **Data Validation**: Ensures proper input formats for all fields
- **Excel Export**: Automatically saves interview results to `interview_database.xlsx`
- **Progress Tracking**: Visual progress indicator during interviews
- **Local AI Model**: Uses Phi-3 model via llama-cpp-python (no API keys required)

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- At least 4GB RAM (8GB recommended)
- ~2GB free disk space for the model

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/ShadowMonarch001/AI-Interview-Chatbot-Assignment.git
   cd AI-Interview-Chatbot-Assignment
   ```

2. **Create a virtual environment**
   ```bash
   # On Windows
   python -m venv venv
   venv\Scripts\activate

   # On macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Download the AI Model**
   
   Download the Phi-3 mini GGUF model file:
   - **Direct Download**: [Phi-3-mini-4k-instruct-q4.gguf](https://huggingface.co/microsoft/Phi-3-mini-4k-instruct-gguf/tree/main)
   - **File Size**: ~2.4GB

   Place the downloaded file in your project root directory.

5. **Run the application**
   ```bash
   streamlit run app.py
   ```

   The app will open in your browser at `http://localhost:8501`

## 📦 Dependencies

Create a `requirements.txt` file with the following dependencies:

```txt
streamlit==1.29.0
pandas==2.1.4
openpyxl==3.1.2
llama-cpp-python==0.2.20
```

### Installing llama-cpp-python with GPU Support (Optional)

For better performance with NVIDIA GPUs:

```bash
# Uninstall CPU version first
pip uninstall llama-cpp-python

# Install with CUDA support
CMAKE_ARGS="-DLLAMA_CUBLAS=on" pip install llama-cpp-python --no-cache-dir
```

For Apple Silicon Macs:
```bash
CMAKE_ARGS="-DLLAMA_METAL=on" pip install llama-cpp-python --no-cache-dir
```

## 🔧 Configuration

### Model Configuration

The model configuration can be adjusted in the `load_model()` function:

```python
return Llama(
    model_path="Phi-3-mini-4k-instruct-q4.gguf",  # Path to your model
    n_ctx=4096,        # Context window size
    n_threads=8,       # CPU threads (adjust based on your system)
    n_gpu_layers=20,   # GPU layers (0 for CPU-only)
    temperature=0.3,   # Lower = more consistent, Higher = more creative
    top_p=0.9         # Nucleus sampling parameter
)
```

### Validation Rules

- **Name**: Letters and spaces only, minimum 2 characters
- **Email**: Valid email format (user@domain.com)
- **Phone**: Exactly 9 digits
- **Experience**: 0-50 years
- **Questions**: Minimum 10 characters, must end with '?'

## 📊 Data Storage

Interview data is automatically saved to `interview_database.xlsx` with the following structure:

| Column | Description |
|--------|-------------|
| Full Name | Candidate's full name |
| Email | Email address |
| Phone | Phone number |
| Experience | Years of experience |
| Desired Position | Target job role |
| Location | Current location |
| Tech Stack | Comma-separated technologies |
| Q1-Q5 | Interview questions |
| A1-A5 | Candidate answers |
| Interview_Date | Date of interview |
| Interview_Time | Time of interview |

## 🎯 Usage Flow

1. **Start Interview**: Candidate provides personal information
2. **Tech Profile**: System collects experience level and tech stack
3. **Question Generation**: AI generates 5 personalized technical questions
4. **Interview Conduct**: Candidate answers questions in sequence
5. **Data Export**: Results automatically saved to Excel

## 🛠️ Customization

### Changing Question Count

Update the question generation logic to produce more or fewer questions by modifying the range in `generate_interview_questions()`.

### Custom Validation Rules

Modify the validator functions (`valid_name`, `valid_email`, etc.) to change input requirements.

## 🔍 Troubleshooting

### Common Issues

1. **Model not loading**
   - Ensure the GGUF file is in the correct location
   - Check available RAM (model requires ~4GB)
   - Verify file isn't corrupted by checking file size

2. **Slow performance**
   - Reduce `n_gpu_layers` if using GPU
   - Decrease `n_ctx` for lower memory usage
   - Close other memory-intensive applications

3. **Excel writing errors**
   - Close the Excel file if it's open
   - Check write permissions in the directory
   - Ensure openpyxl is properly installed

### Performance Tips

- Use GPU acceleration when available
- Adjust `n_threads` based on your CPU cores
- Lower `temperature` for more consistent outputs
- Increase `n_gpu_layers` if you have sufficient VRAM

**Note**: This application runs entirely locally 
