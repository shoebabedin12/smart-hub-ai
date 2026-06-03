# ১. পাইথনের অফিশিয়াল ইমেজ ব্যবহার করছি
FROM python:3.10-slim

# ২. ডকার কন্টেনারের ভেতরে ওয়ার্কিং ডিরেক্টরি সেট করছি
WORKDIR /app

# ৩. সিস্টেমের কিছু প্রয়োজনীয় টুলস ইন্সটল করছি (FAISS এবং PyMuPDF এর জন্য)
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# ৪. রিকোয়ারমেন্টস ফাইলটি কপি করে লাইব্রেরিগুলো ইন্সটল করছি
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ৫. আপনার প্রোজেক্টের বাকি সব ফাইল কপি করছি
COPY . .

# 🎯 হাগিং ফেস স্পেসের পোর্ট সেটআপ (এটি খুব গুরুত্বপূর্ণ)
ENV PORT=7860
EXPOSE 7860

# 🚀 Gunicorn দিয়ে ফ্লাস্ক অ্যাপ রান করা (আপনার মেইন ফাইলের নাম app.py এবং ফ্লাস্ক ভ্যারিয়েবল app হলে)
CMD ["gunicorn", "-b", "0.0.0.0:7860", "app:app", "--timeout", "300"]