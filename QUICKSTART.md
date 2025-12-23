# 🚀 Quick Start Guide

## Installation (5 minutes)

### Step 1: Run Setup Script
```powershell
cd c:\Users\sberker\Downloads\Advanced_Programming
.\setup.ps1
```

This will:
- ✓ Check Python version
- ✓ Create virtual environment
- ✓ Install all dependencies
- ✓ Create .env file

### Step 2: Configure API Key
1. Open `.env` file in a text editor
2. Replace `your_openai_api_key_here` with your actual OpenAI API key
3. Get a key from: https://platform.openai.com/api-keys

Example:
```env
OPENAI_API_KEY=sk-proj-abc123def456...
```

### Step 3: Launch the Application
```powershell
streamlit run app.py
```

Your browser will open automatically at `http://localhost:8501`

---

## Using the Application (3 minutes)

### Test with Sample Data
1. Click **"Load Sample Project Data"** button on the home screen
2. OR upload your own CSV file using the sidebar

### Explore Features

**Tab 1: Gantt Chart**
- View interactive project timeline
- Hover over tasks for details
- Color-coded by risk level

**Tab 2: Resource Analysis**
- See workload distribution
- Identify over/under-utilized resources
- View cost breakdown

**Tab 3: Risk Distribution**
- Pie chart of risk levels
- Table of high-risk tasks

**Tab 4: AI Agent Analysis**
- Click **"Run AI Agent Analysis"**
- Wait 1-3 minutes for AI to complete
- Review detailed insights
- Download report

---

## Your First Analysis (10 minutes)

1. **Upload CSV**: Use `dummy_data.csv` or your own file
2. **Review Visualizations**: Check Gantt chart and metrics
3. **Run AI Analysis**: Click the blue button in AI Agent tab
4. **Read Insights**: Review risk and resource recommendations
5. **Download Report**: Save the analysis for documentation

---

## Troubleshooting

**Problem**: Streamlit won't start  
**Fix**: Ensure virtual environment is activated:
```powershell
.\venv\Scripts\Activate.ps1
streamlit run app.py
```

**Problem**: API Error  
**Fix**: Check your `.env` file has valid OpenAI key

**Problem**: CSV Error  
**Fix**: Ensure CSV has all required columns (see README.md)

---

## Key Features

✅ **Multi-Agent AI**: Two specialized agents (Risk + Resource)  
✅ **Interactive Gantt Chart**: Drag, zoom, and hover  
✅ **Cost Tracking**: Automatic calculation  
✅ **Risk Assessment**: AI-powered analysis  
✅ **Resource Optimization**: Workload balancing  
✅ **Export Reports**: Download AI insights  

---

## Project Structure

```
📁 Advanced_Programming/
├── 📄 app.py              ← Main dashboard
├── 📄 agents.py           ← AI agent logic
├── 📄 dummy_data.csv      ← Sample data
├── 📄 requirements.txt    ← Dependencies
├── 📄 .env                ← Your API key (you create this)
└── 📄 README.md           ← Full documentation
```

---

## What Makes This Special?

🎯 **Production-Quality Code**
- Type hints throughout
- Extensive error handling
- Clean architecture

🧠 **Advanced AI Integration**
- Real CrewAI multi-agent system
- Custom tools for domain analysis
- Sequential task orchestration

📊 **Professional UI/UX**
- Responsive design
- Interactive visualizations
- Real-time updates

🎓 **AI4SE Compliant**
- Phase-aligned comments
- Best practices
- Academic rigor

---

## Next Steps

1. ✅ Run setup script
2. ✅ Add API key to `.env`
3. ✅ Launch application
4. ✅ Upload project data
5. ✅ Run AI analysis
6. 🎉 Present your MVP!

---

## Getting Help

- **Full Documentation**: See `README.md`
- **Code Comments**: Extensively documented in `agents.py` and `app.py`
- **Sample Data**: Use `dummy_data.csv` to understand format

---

**Estimated Total Time: 20 minutes from setup to first analysis**

Good luck with your university project! 🎓✨
