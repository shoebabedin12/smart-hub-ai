# ১. পাইথনের অফিশিয়াল লাইটওয়েট ইমেজ
FROM python:3.10-slim

# ২. কন্টেইনারের ভেতরের ডিরেক্টরি সেট করা
WORKDIR /app

# ৩. সিস্টেমের প্রয়োজনীয় সি++ এবং FAISS কম্পাইলার টুলস ইনস্টল করা
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# ৪. পিপ (pip) আপডেট করা এবং রিকোয়ারমেন্টস ফাইল কপি করা
RUN pip install --no-cache-dir --upgrade pip
COPY requirements.txt .

# 🎯 এখানে আমরা আলাদা করে gunicorn ইনস্টল নিশ্চিত করছি যেন PATH এরর না আসে
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir gunicorn

# ৫. প্রজেক্টের বাকি সব ফাইল কপি করা
COPY . .

# 🌐 হাগিং ফেসের পোর্ট কনফিগারেশন
ENV PORT=7860
EXPOSE 7860

# 🚀 Gunicorn দিয়ে ফ্লাস্ক অ্যাপ রান করা 
# (এখানে app:app মানে আপনার মেইন ফাইলের নাম app.py এবং ভেতরে Flask অবজেক্টের নাম app)
CMD ["gunicorn", "-b", "0.0.0.0:7860", "app:app", "--timeout", "300", "--workers", "2"]