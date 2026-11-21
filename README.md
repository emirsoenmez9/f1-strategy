# f1-strategy
Gerçek F1 yarış verisinden lastik aşınmasını istatistiksel olarak modellemek ve bu modeli Monte Carlo simülasyonuyla birleştirip, belirsizlik altında hangi pit-stop stratejisinin daha hızlı olduğunu karşılaştırmak.
Yani kısaca bir yarışta 1 pit mi yoksa 2 pit mi yapmak daha avantajlı ve bu sonuçtan ne kadar emin olabiliriz.
OpenF1'den açık kaynaklı veriler çekildi. 
Çoklu regresyon ile her lastiğin her tur ne kadar yavaşladığı tahmin edilir. 
Monte Carlo simülasyonuyla ortalama süreler ile kıyaslanır. 
