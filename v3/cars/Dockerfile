# Base image olarak Python 3.8 slim kullanıyoruz
FROM python:3.8-slim

# Çalışma dizini belirleniyor
WORKDIR /app

# requirements.txt dosyasını kopyalayın ve bağımlılıkları yükleyin
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

# Uygulama dosyalarını kopyalayın
COPY . .

# Servisin çalışacağı portu expose edin
EXPOSE 8070

# Uygulama dosyasını çalıştırın
CMD ["python", "service.py"]
