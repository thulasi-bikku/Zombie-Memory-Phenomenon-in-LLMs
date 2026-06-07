# 🧠 The Zombie Memory Phenomenon in LLMs

## 📌 Overview
This project explores a critical security vulnerability in Large Language Models (LLMs) called the **"Zombie Memory Phenomenon"** — where supposedly "forgotten" data resurfaces after model compression.

The work investigates how **machine unlearning** interacts with **post-training quantization**, revealing that unlearned data is not truly erased but masked — and can reappear when models are compressed.

📄 Based on the research paper:  
"The Zombie Memory Phenomenon: How Post-Training Quantization Shatters Machine Unlearning Masks in Large Language Models"

---

## 🚀 Key Idea

- Machine Unlearning tries to remove sensitive data from models.
- Quantization reduces model size for deployment.
- ⚠️ Combining both leads to **data leakage risk**.

👉 The core finding:
> Quantization breaks the "safety mask" created during unlearning, causing hidden data to reappear.

---

## 🧪 Experimental Pipeline

1. **Baseline Model**
   - GPT-2 Small (124M parameters)

2. **Memorization Phase**
   - Model trained to memorize a secret token

3. **Unlearning Phase**
   - Gradient-based unlearning applied
   - Goal: Remove memorized data

4. **Quantization Phase**
   - 4-bit Min-Max Quantization applied
   - Observation: Data resurfaces

---

## 📊 Key Results

| Phase                | Safety Perplexity | Data Leakage |
|---------------------|------------------|--------------|
| Memorized Model     | 1.0              | 100%         |
| Unlearned Model     | >3.4 Million     | 0.0%         |
| Quantized Model     | 1.0              | 4.0%         |

📌 Insight:
- Unlearning appears successful at high precision.
- Quantization **revives hidden knowledge**.

---

## 🔍 Core Concepts

### 1. Machine Unlearning
Removes specific data from trained models without retraining.

### 2. Quantization
Reduces model precision (e.g., 16-bit → 4-bit) to save memory.

### 3. Zombie Memory
Previously "deleted" information that **comes back to life** after quantization.

---

## ⚙️ Technologies Used

- Python
- PyTorch / Transformers
- GPT-2 Architecture
- AutoGPTQ / BitsAndBytes
- Membership Inference Attacks (MIA)

---

## 🧠 Key Contributions

- ✅ Demonstrated that unlearning creates a **mask, not deletion**
- ✅ Introduced the **Zombie Memory Phenomenon**
- ✅ Showed **quantization breaks safety guarantees**
- ✅ Provided **security analysis using MIA attacks**
- ✅ Proposed **quantization-aware validation strategies**

---

## ⚠️ Security Implications

- Models considered "safe" can leak data after deployment
- Risk increases in:
  - Edge AI devices
  - Compressed LLM deployments
- Highlights need for:
  - 🔐 Robust unlearning methods
  - 🧪 Post-quantization testing

---

## 📂 Project Structure

```
├── notebooks/
│   └── quantization_resilient_machine_unlearning.ipynb
├── paper/
│   └── Zombie_Memory_Phenomenon.pdf
├── results/
│   ├── graphs/
│   └── metrics/
├── README.md
```

---

## ▶️ How to Run

1. Clone the repository:
```bash
git clone https://github.com/your-username/zombie-memory-llm.git
cd zombie-memory-llm
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the notebook:
```bash
jupyter notebook
```

---

## 📈 Future Work

- Develop **quantization-resistant unlearning**
- Improve robustness of safety mechanisms
- Explore **real-world LLM deployments**
- Extend to larger models (e.g., LLaMA, GPT variants)

---

## 👨‍💻 Authors

- Pavan Kumar Gembali  
- Gompa Viswanadh Naidu  
- Peta Sashi Vardhan  
- Chakrika Gurrala  
- Thulasi Bikku  
- Srinivasarao Thota  

---

## 📜 License

This project is for research and academic purposes.

---

## ⭐ Acknowledgements

- Inspired by recent work in:
  - Machine Unlearning
  - LLM Safety
  - Model Compression

---

## 📬 Contact

For queries or collaboration:  
📧 pavangembali945@gmail.com

---
