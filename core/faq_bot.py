def cevapla(soru):
    soru = soru.lower()
    if "çalışma saatleri" in soru:
        return "Servisimiz hafta içi her gün 09:00 - 18:00 saatleri arasında hizmet vermektedir."
    elif "adres" in soru or "nerede" in soru:
        return "Servisimiz Hacettepe Mahallesi, Beytepe Kampüsü içinde bulunmaktadır."
    elif "ücret" in soru:
        return "Servis ücreti aracın türüne ve yapılacak işleme göre değişmektedir."
    elif "randevu" in soru:
        return "Randevu almak için formu doldurabilir veya doğrudan mesaj atabilirsiniz."
    else:
        return "Maalesef bu soruya şu an yanıt veremiyorum. Daha sonra tekrar deneyin."

if __name__ == "__main__":
    while True:
        kullanici_sorusu = input("Soru: ")
        if kullanici_sorusu.lower() in ["çık", "exit", "q"]:
            break
        yanit = cevapla(kullanici_sorusu)
        print("Yanıt:", yanit)
