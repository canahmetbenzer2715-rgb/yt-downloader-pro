import sys
import os
import yt_dlp
import requests # Güncelleme kontrolü için gerekli
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                             QLineEdit, QPushButton, QLabel, QMessageBox, 
                             QFileDialog, QComboBox, QScrollArea, QFrame, 
                             QRadioButton, QButtonGroup, QDialog, QProgressBar)
from PyQt6.QtCore import QThread, pyqtSignal, Qt, QSize
from PyQt6.QtGui import QIcon, QFont, QPixmap

# --- GÜNCELLEME AYARLARI ---
# GitHub'dan aldığın linkleri buraya yapıştır!
MEVCUT_VERSIYON = "1.0.0"
VERSION_URL = "https://raw.githubusercontent.com/canahmetbenzer2715-rgb/REPO_ADIN/main/version.txt"
UPDATE_URL = "https://raw.githubusercontent.com/canahmetbenzer2715-rgb/REPO_ADIN/main/main.py"

# --- Kaydırmayı Tamamen Engelleyen Özel Sınıf ---
class NoScrollArea(QScrollArea):
    def wheelEvent(self, event):
        event.ignore()

# --- Güncelleme İşlemi Sınıfı ---
class GuncellemeIslemi(QThread):
    durum = pyqtSignal(str)
    bitti = pyqtSignal(bool)

    def run(self):
        try:
            self.durum.emit("Güncelleme kontrol ediliyor...")
            v_yanit = requests.get(VERSION_URL, timeout=5)
            if v_yanit.status_code == 200:
                yeni_v = v_yanit.text.strip()
                if yeni_v != MEVCUT_VERSIYON:
                    self.durum.emit(f"Yeni sürüm ({yeni_v}) indiriliyor...")
                    k_yanit = requests.get(UPDATE_URL, timeout=10)
                    if k_yanit.status_code == 200:
                        mevcut_dosya = sys.argv[0]
                        yeni_dosya = mevcut_dosya + ".new"
                        with open(yeni_dosya, "wb") as f:
                            f.write(k_yanit.content)
                        
                        self.durum.emit("Güncelleme hazır! Yeniden başlatılıyor...")
                        
                        # Windows için değiştirici script oluştur
                        with open("update.bat", "w") as f:
                            f.write(f'@echo off\ntimeout /t 2 /nobreak > nul\ndel "{mevcut_dosya}"\nrename "{yeni_dosya}" "{os.path.basename(mevcut_dosya)}"\nstart "" "{os.path.basename(mevcut_dosya)}"\ndel "%~f0"')
                        
                        os.startfile("update.bat")
                        self.bitti.emit(True)
                    else: self.durum.emit("Kod indirilemedi.")
                else: self.durum.emit("Zaten güncel sürümdesiniz.")
            else: self.durum.emit("Sunucuya bağlanılamadı.")
        except Exception as e: self.durum.emit(f"Hata: {str(e)}")

# --- Profesyonel Hata Penceresi ---
class ProHataMesaji(QDialog):
    def __init__(self, baslik, mesaj, alt_mesaj, ebeveyn=None):
        super().__init__(ebeveyn)
        self.setWindowTitle(baslik)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setModal(True)
        self.setFixedSize(450, 220)
        self.setStyleSheet("background-color: #121212; border: 2px solid #ff0000; border-radius: 15px;")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        baslik_label = QLabel(baslik.upper())
        baslik_label.setStyleSheet("color: #ff0000; font-size: 18px; font-weight: bold; border: none; background: transparent;")
        baslik_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(baslik_label)

        temiz_mesaj = "FFmpeg bulunamadı! Lütfen ffmpeg klasörünün 'main.py' ile aynı yerde olduğundan emin olun." if "ffmpeg" in mesaj.lower() else mesaj

        mesaj_label = QLabel(temiz_mesaj)
        mesaj_label.setWordWrap(True)
        mesaj_label.setStyleSheet("color: #ffffff; font-size: 14px; font-weight: 600; border: none; margin-top: 10px; background: transparent;")
        mesaj_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(mesaj_label)

        alt_label = QLabel(alt_mesaj)
        alt_label.setStyleSheet("color: #aaaaaa; font-size: 11px; border: none; font-style: italic; background: transparent;")
        alt_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(alt_label)

        layout.addStretch()

        self.btn_tamam = QPushButton("ANLADIM")
        self.btn_tamam.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_tamam.setFixedHeight(45)
        self.btn_tamam.setStyleSheet("""
            QPushButton {
                background-color: #ff0000; color: white; border-radius: 10px; font-weight: bold; font-size: 14px; border: none;
            }
            QPushButton:hover { background-color: #cc0000; }
        """)
        self.btn_tamam.clicked.connect(self.accept)
        layout.addWidget(self.btn_tamam)

# --- Profesyonel Başarı Penceresi ---
class ProOnayMesaji(QDialog):
    def __init__(self, baslik, mesaj, alt_mesaj, ebeveyn=None):
        super().__init__(ebeveyn)
        self.setWindowTitle(baslik)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setModal(True)
        self.setFixedSize(450, 220)
        self.setStyleSheet("background-color: #121212; border: 2px solid #00ff00; border-radius: 15px;")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        baslik_label = QLabel(baslik.upper())
        baslik_label.setStyleSheet("color: #00ff00; font-size: 18px; font-weight: bold; border: none; background: transparent;")
        baslik_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(baslik_label)

        mesaj_label = QLabel(mesaj)
        mesaj_label.setWordWrap(True)
        mesaj_label.setStyleSheet("color: #ffffff; font-size: 14px; font-weight: 600; border: none; margin-top: 10px; background: transparent;")
        mesaj_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(mesaj_label)

        alt_label = QLabel(alt_mesaj)
        alt_label.setStyleSheet("color: #aaaaaa; font-size: 11px; border: none; font-style: italic; background: transparent;")
        alt_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(alt_label)

        layout.addStretch()

        self.btn_tamam = QPushButton("HARİKA")
        self.btn_tamam.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_tamam.setFixedHeight(45)
        self.btn_tamam.setStyleSheet("""
            QPushButton {
                background-color: #00ff00; color: black; border-radius: 10px; font-weight: bold; font-size: 14px; border: none;
            }
            QPushButton:hover { background-color: #00cc00; }
        """)
        self.btn_tamam.clicked.connect(self.accept)
        layout.addWidget(self.btn_tamam)

class IndirmeIslemi(QThread):
    sonuc = pyqtSignal(str)
    ilerleme = pyqtSignal(dict)

    def __init__(self, url, klasör, ayarlar):
        super().__init__()
        self.url = url
        self.klasör = klasör
        self.ayarlar = ayarlar

    def progress_hook(self, d):
        if d['status'] == 'downloading':
            try:
                toplam_bayt = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
                indirilen_bayt = d.get('downloaded_bytes', 0)
                hiz = d.get('speed', 0) # bayt/s
                kalan_sure = d.get('eta', 0) # saniye
                
                if toplam_bayt > 0:
                    yuzde = int((indirilen_bayt / toplam_bayt) * 100)
                else:
                    yuzde = 0
                
                indirilen_mb = indirilen_bayt / (1024 * 1024)
                toplam_mb = toplam_bayt / (1024 * 1024)
                hiz_mb = (hiz / (1024 * 1024)) if hiz else 0
                
                # Saniyeyi dk:sn formatına çevir
                if kalan_sure:
                    dakika, saniye = divmod(kalan_sure, 60)
                    eta_str = f"{int(dakika)}dk {int(saniye)}sn"
                else:
                    eta_str = "Hesaplanıyor..."

                self.ilerleme.emit({
                    'yuzde': yuzde,
                    'indirilen': indirilen_mb,
                    'toplam': toplam_mb,
                    'hiz': hiz_mb,
                    'kalan': eta_str
                })
            except:
                pass

    def run(self):
        mevcut_dizin = os.path.dirname(os.path.abspath(__file__))
        
        yollar = [
            os.path.join(mevcut_dizin, 'ffmpeg', 'bin', 'ffmpeg.exe'),
            os.path.join(mevcut_dizin, 'bin', 'ffmpeg.exe'),
            os.path.join(mevcut_dizin, 'ffmpeg.exe'),
            os.path.join(mevcut_dizin, 'ffmpeg', 'ffmpeg.exe'),
            'ffmpeg' 
        ]
        
        ffmpeg_final_yol = None
        for yol in yollar:
            if os.path.exists(yol):
                ffmpeg_final_yol = yol
                break

        if not ffmpeg_final_yol and os.name == 'nt':
             self.sonuc.emit("FFmpeg Bulunamadı")
             return

        cikti_sablonu = os.path.join(self.klasör, '%(title).100s.%(ext)s')
        mod = self.ayarlar['mod']
        
        ydl_opts = {
            'outtmpl': cikti_sablonu,
            'noplaylist': True,
            'quiet': True,
            'no_warnings': True,
            'progress_hooks': [self.progress_hook],
            'ffmpeg_location': ffmpeg_final_yol if ffmpeg_final_yol != 'ffmpeg' else None,
        }

        if mod == "mp3":
            ydl_opts.update({
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
            })
        else:
            kalite = self.ayarlar['kalite']
            ydl_opts.update({
                'format': f'bestvideo[height<={kalite}][ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
                'merge_output_format': 'mp4'
            })

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                self.ilerleme.emit({'yuzde': 0, 'indirilen': 0, 'toplam': 0, 'hiz': 0, 'kalan': ""})
                ydl.download([self.url])
            self.sonuc.emit("Başarılı")
        except Exception as e:
            self.sonuc.emit(str(e))

class YouTubeDownloader(QWidget):
    def __init__(self):
        super().__init__()
        self.secilen_klasör = os.path.join(os.path.expanduser("~"), "Downloads")
        self.old_pos = None 
        self.icon_path = "app_icon.ico.png"
        self.initUI()

    def initUI(self):
        self.setWindowTitle('YTPro Video İndirici')
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint) 
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, False)
        self.setMinimumSize(540, 880) # Güncelleme butonu için yüksekliği biraz daha artırdım

        self.setStyleSheet("""
            QWidget { background-color: #0f0f0f; color: #ffffff; font-family: 'Segoe UI', sans-serif; }
            QLabel { font-size: 12px; font-weight: bold; color: #aaaaaa; margin-top: 15px; text-transform: uppercase; }
            QLineEdit { padding: 15px; background-color: #1a1a1a; border: 2px solid #222; border-radius: 12px; color: white; font-size: 14px; }
            QLineEdit:focus { border: 2px solid #00ff00; }
            QComboBox { background-color: #1a1a1a; border: 2px solid #222; padding: 10px; color: white; border-radius: 12px; min-height: 50px; }
            
            QRadioButton#menuIconBtn { 
                background-color: #1a1a1a; 
                border: 2px solid #222; 
                border-radius: 15px; 
                padding: 10px; 
                color: #888; 
                font-weight: bold;
                text-align: center;
            }
            QRadioButton#menuIconBtn::indicator { width: 0px; height: 0px; } 
            QRadioButton#menuIconBtn:checked { 
                border: 2px solid #00ff00; 
                background-color: #1a2a1a; 
                color: #00ff00;
            }
            QRadioButton#menuIconBtn:hover { background-color: #252525; }

            QRadioButton { color: #aaa; font-size: 13px; font-weight: bold; padding: 8px; }
            QRadioButton:checked { color: #00ff00; }
            
            QPushButton#indirBtn { 
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #00ff00, stop:1 #008800); 
                color: black; font-size: 18px; font-weight: 800; min-height: 70px; border-radius: 18px; margin-top: 20px; border: none;
            }
            QPushButton#indirBtn:hover { background: #00ff66; }
            QPushButton#indirBtn:disabled { background: #333; color: #777; }

            #guncelleBtn {
                background-color: #1a1a1a; color: #00ff00; border: 1px solid #00ff00; border-radius: 10px; min-height: 35px; font-weight: bold; margin-top: 10px;
            }
            #guncelleBtn:hover { background-color: #00ff00; color: black; }
            
            QPushButton#kucukBtn { 
                background-color: #f1c40f; color: #000; border-radius: 10px; min-height: 40px; font-weight: bold; border: none;
            }
            QPushButton#kucukBtn:hover { background-color: #f39c12; }
            
            QPushButton#sysBtn { background-color: transparent; border: none; font-size: 20px; font-weight: bold; color: #555; padding: 5px; }
            QPushButton#sysBtn:hover { color: #ffffff; background-color: #333333; }
            
            QPushButton#closeBtn { background-color: transparent; border: none; font-size: 16px; color: #555; }
            QPushButton#closeBtn:hover { color: #ffffff; background-color: #e81123; }
            
            QLabel#klasorYolu { font-size: 11px; color: #777; background: #161616; padding: 12px; border-radius: 12px; border: 1px dashed #333; }
            QFrame#altMenu { background-color: #161616; border-radius: 10px; padding: 10px; margin-top: 5px; }
            
            QProgressBar {
                border: 2px solid #222; border-radius: 10px; background-color: #1a1a1a;
                text-align: center; color: white; height: 18px; margin-top: 10px; font-size: 10px; font-weight: bold;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #00ff00, stop:1 #008800);
                border-radius: 8px;
            }
        """)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Başlık Çubuğu
        title_bar = QFrame()
        title_bar.setFixedHeight(45)
        title_bar.setStyleSheet("background-color: #0a0a0a;")
        title_layout = QHBoxLayout(title_bar)
        title_layout.setContentsMargins(15, 0, 0, 0)
        title_layout.setSpacing(10) 
        
        window_title = QLabel("YTPro Video İndirici")
        window_title.setStyleSheet("color: #666; font-size: 11px; margin-top: 0px; text-transform: none; border: none; background: transparent;")
        title_layout.addWidget(window_title)
        title_layout.addStretch()

        btn_min = QPushButton("-")
        btn_min.setObjectName("sysBtn")
        btn_min.setFixedWidth(45)
        btn_min.setFixedHeight(45)
        btn_min.clicked.connect(self.showMinimized)
        title_layout.addWidget(btn_min)

        btn_close = QPushButton("✕")
        btn_close.setObjectName("closeBtn")
        btn_close.setFixedWidth(45)
        btn_close.setFixedHeight(45)
        btn_close.clicked.connect(self.close)
        title_layout.addWidget(btn_close)

        main_layout.addWidget(title_bar)

        scroll = NoScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(35, 20, 35, 30)

        # GÜNCELLEME BUTONU (YENİ)
        self.btn_guncelle = QPushButton(f"🔄 SİSTEMİ GÜNCELLE (v{MEVCUT_VERSIYON})")
        self.btn_guncelle.setObjectName("guncelleBtn")
        self.btn_guncelle.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_guncelle.clicked.connect(self.guncellemeyi_denetle)
        layout.addWidget(self.btn_guncelle)

        layout.addWidget(QLabel('🔗 Video Bağlantısı'))
        self.input = QLineEdit()
        self.input.setPlaceholderText("URL'yi buraya yapıştırın...")
        layout.addWidget(self.input)

        layout.addWidget(QLabel('📂 İçerik Türü'))
        
        self.ana_tur_combo = QComboBox()
        self.ana_tur_combo.addItem(QIcon(self.icon_path), " YouTube")
        self.ana_tur_combo.setIconSize(QSize(20, 20))
        layout.addWidget(self.ana_tur_combo)

        self.yt_alt_frame = QFrame()
        self.yt_alt_frame.setObjectName("altMenu")
        alt_layout = QHBoxLayout(self.yt_alt_frame)
        self.yt_grubu = QButtonGroup(self)

        self.radio_video = QRadioButton(" VIDEO")
        self.radio_video.setObjectName("menuIconBtn")
        self.radio_video.setIcon(QIcon(self.icon_path))
        self.radio_video.setIconSize(QSize(20, 20))
        self.radio_video.setChecked(True)

        self.radio_shorts = QRadioButton(" SHORTS")
        self.radio_shorts.setObjectName("menuIconBtn")
        self.radio_shorts.setIcon(QIcon(self.icon_path))
        self.radio_shorts.setIconSize(QSize(20, 20))

        self.yt_grubu.addButton(self.radio_video)
        self.yt_grubu.addButton(self.radio_shorts)
        
        alt_layout.addWidget(self.radio_video)
        alt_layout.addWidget(self.radio_shorts)
        layout.addWidget(self.yt_alt_frame)

        layout.addWidget(QLabel('💾 Dosya Formatı'))
        format_layout = QHBoxLayout()
        self.format_grubu = QButtonGroup(self)
        self.radio_mp4 = QRadioButton("🎬 MP4 (Video)")
        self.radio_mp3 = QRadioButton("🎵 MP3 (Ses)")
        self.radio_mp4.setChecked(True)
        self.format_grubu.addButton(self.radio_mp4)
        self.format_grubu.addButton(self.radio_mp3)
        format_layout.addWidget(self.radio_mp4)
        format_layout.addWidget(self.radio_mp3)
        layout.addLayout(format_layout)
        self.radio_mp3.toggled.connect(self.arayuz_guncelle)

        self.kalite_label = QLabel('⚙️ Çözünürlük Seçimi')
        layout.addWidget(self.kalite_label)
        self.kalite_combo = QComboBox()
        self.kalite_combo.addItems(["2160p (4K)", "1440p (2K)", "1080p (Full HD)", "720p (HD)", "480p (SD)"])
        self.kalite_combo.setCurrentIndex(2)
        layout.addWidget(self.kalite_combo)

        layout.addWidget(QLabel('📂 Kayıt Klasörü'))
        klasor_layout = QHBoxLayout()
        self.klasor_info = QLabel(self.secilen_klasör)
        self.klasor_info.setObjectName("klasorYolu")
        self.btn_klasor = QPushButton("GÖZAT")
        self.btn_klasor.setFixedWidth(80)
        self.btn_klasor.setObjectName("kucukBtn")
        self.btn_klasor.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_klasor.clicked.connect(self.klasor_sec)
        klasor_layout.addWidget(self.klasor_info, 4)
        klasor_layout.addWidget(self.btn_klasor, 1)
        layout.addLayout(klasor_layout)

        layout.addStretch()

        self.btn_indir = QPushButton('İNDİRMEYİ BAŞLAT')
        self.btn_indir.setObjectName("indirBtn")
        self.btn_indir.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_indir.clicked.connect(self.baslat)
        layout.addWidget(self.btn_indir)

        self.pbar = QProgressBar()
        self.pbar.setVisible(False)
        layout.addWidget(self.pbar)

        # Gelişmiş Bilgi Etiketi (Hız, MB, Kalan Süre)
        self.pbar_label = QLabel("")
        self.pbar_label.setStyleSheet("color: #00ff00; font-size: 11px; margin-top: 5px; font-weight: bold; background: #1a1a1a; padding: 10px; border-radius: 8px;")
        self.pbar_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.pbar_label.setVisible(False)
        layout.addWidget(self.pbar_label)

        scroll.setWidget(container)
        main_layout.addWidget(scroll)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.old_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if self.old_pos is not None:
            delta = event.globalPosition().toPoint() - self.old_pos
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.old_pos = event.globalPosition().toPoint()

    def mouseReleaseEvent(self, event):
        self.old_pos = None

    def arayuz_guncelle(self):
        is_mp3 = self.radio_mp3.isChecked()
        self.kalite_label.setVisible(not is_mp3)
        self.kalite_combo.setVisible(not is_mp3)

    def klasor_sec(self):
        folder = QFileDialog.getExistingDirectory(self, "Klasör Seç")
        if folder:
            self.secilen_klasör = folder
            self.klasor_info.setText(folder if len(folder) < 40 else "..." + folder[-37:])

    # GÜNCELLEME BAŞLATMA FONKSİYONU
    def guncellemeyi_denetle(self):
        self.g_islem = GuncellemeIslemi()
        self.g_islem.durum.connect(lambda m: self.pbar_label.setText(m))
        self.pbar_label.setVisible(True)
        self.btn_guncelle.setEnabled(False)
        self.g_islem.start()

    def baslat(self):
        url = self.input.text().strip()
        if not url:
            hata = ProHataMesaji("UYARI", "Bağlantı alanı boş bırakılamaz!", "Lütfen bir link girin.", self)
            hata.exec()
            return

        secilen_shorts = self.radio_shorts.isChecked()
        url_shorts_mu = "/shorts/" in url.lower()

        if secilen_shorts and not url_shorts_mu:
            hata = ProHataMesaji("LİNK HATASI", "Bu bir Shorts linki değil!", "Lütfen Shorts kategorisine uygun bir link girin.", self)
            hata.exec()
            return
        
        if not secilen_shorts and url_shorts_mu:
            hata = ProHataMesaji("LİNK HATASI", "Bu bir normal video linki değil!", "Lütfen Video kategorisine uygun bir link girin.", self)
            hata.exec()
            return
        
        ayarlar = {
            'mod': "mp3" if self.radio_mp3.isChecked() else "mp4",
            'tur': "shorts" if secilen_shorts else "video",
            'kalite': "".join(filter(str.isdigit, self.kalite_combo.currentText()))
        }
        
        self.btn_indir.setEnabled(False)
        self.btn_indir.setText("🚀 HAZIRLANIYOR...")
        self.pbar.setVisible(True)
        self.pbar.setValue(0)
        self.pbar_label.setVisible(True)
        self.pbar_label.setText("Bağlantı Kuruluyor...")

        self.islem = IndirmeIslemi(url, self.secilen_klasör, ayarlar)
        self.islem.sonuc.connect(self.tamamlandi)
        self.islem.ilerleme.connect(self.ilerleme_guncelle)
        self.islem.start()

    def ilerleme_guncelle(self, veri):
        self.pbar.setValue(veri['yuzde'])
        if veri['toplam'] > 0:
            bilgi_metni = (f"📥 {veri['indirilen']:.1f} MB / {veri['toplam']:.1f} MB\n"
                           f"⚡ Hız: {veri['hiz']:.2f} MB/s  |  ⏳ Kalan: {veri['kalan']}")
            self.pbar_label.setText(bilgi_metni)
        else:
            self.pbar_label.setText(f"İndiriliyor: {veri['indirilen']:.1f} MB...")

    def tamamlandi(self, mesaj):
        self.btn_indir.setEnabled(True)
        self.btn_indir.setText("İNDİRMEYİ BAŞLAT")
        self.pbar.setVisible(False)
        self.pbar_label.setVisible(False)
        
        if mesaj == "Başarılı":
            onay = ProOnayMesaji("BAŞARILI", "İndirme işlemi başarıyla tamamlandı!", "Dosyanız seçtiğiniz klasöre kaydedildi.", self)
            onay.exec()
        else:
            hata = ProHataMesaji("SİSTEM HATASI", mesaj, "Hata detayına göre kontrol sağlayın.", self)
            hata.exec()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = YouTubeDownloader()
    ex.show()
    sys.exit(app.exec())