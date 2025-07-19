import os
from dotenv import load_dotenv


from PyQt5.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton,
    QTabWidget, QTextEdit, QFileDialog, QListWidget, QListWidgetItem,
    QLineEdit, QProgressBar, QApplication, QScrollArea
)
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtCore import Qt
from core.parser import parse_multiple_pdfs
from core.embedding import generate_embeddings_for_chunks, upload_embeddings_to_qdrant
from core.summarizer import summarize_chunks


load_dotenv()

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("📄 D2V - Document to Vector AI App")
        self.showMaximized() 
        self.setStyleSheet("background-color: #f3e8ff; font-family: 'Segoe UI';")

        layout = QVBoxLayout()

        header = QHBoxLayout()
        logo = QLabel()
        pixmap = QPixmap("ui/d2v.jpg").scaled(80, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        logo.setPixmap(pixmap)
        logo.setAlignment(Qt.AlignLeft)

        title = QLabel("Document to Vector")
        title.setFont(QFont("Segoe UI", 24, QFont.Bold))
        title.setStyleSheet("color: #5b21b6; margin-left: 20px;")
        title.setAlignment(Qt.AlignVCenter)

        header.addWidget(logo)
        header.addWidget(title)
        header.addStretch()
        layout.addLayout(header)


        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane { border: none; }
            QTabBar::tab {
                background: #e9d5ff;
                padding: 10px 20px;
                border-radius: 8px;
                margin-right: 5px;
                font-weight: bold;
                color: #4c1d95;
            }
            QTabBar::tab:selected {
                background: #c084fc;
                color: white;
            }
        """)
        self.tabs.addTab(self._upload_tab_ui(), "📤 Upload")
        self.tabs.addTab(self._chunk_tab_ui(), "📑 Chunking")
        self.tabs.addTab(self._embedding_tab_ui(), "🧠 Embedding")
        self.tabs.addTab(self._summary_tab_ui(), "📝 Summary")
        self.tabs.addTab(self._settings_tab_ui(), "⚙️ Settings")

        layout.addWidget(self.tabs)
        self.setLayout(layout)

        self.pdf_chunks = []
        self.chunk_titles = []
        self.api_key = ""


    def _upload_tab_ui(self):
        tab = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(15)

        self.upload_label = QLabel("No PDFs uploaded.")
        self.upload_label.setAlignment(Qt.AlignCenter)
        self.upload_label.setStyleSheet("font-size: 16px; color: #6b21a8;")
        layout.addWidget(self.upload_label)

        self.upload_btn = QPushButton("📄 Select PDF(s)")
        self.upload_btn.clicked.connect(self.upload_pdfs)
        self.upload_btn.setStyleSheet("""
            background-color: #9333ea;
            color: white;
            padding: 12px;
            border-radius: 10px;
            font-weight: bold;
        """)
        layout.addWidget(self.upload_btn, alignment=Qt.AlignCenter)

        self.progress = QProgressBar()
        self.progress.setVisible(False)
        self.progress.setStyleSheet("""
            QProgressBar {
                border: 1px solid #d8b4fe;
                border-radius: 5px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #a855f7;
                width: 20px;
            }
        """)
        layout.addWidget(self.progress)

        tab.setLayout(layout)
        return tab

    def upload_pdfs(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Select PDFs", "", "PDF Files (*.pdf)")
        if files:
            self.progress.setVisible(True)
            self.progress.setValue(0)
            chunks_map = parse_multiple_pdfs(files, self.progress)
            self.pdf_chunks = [chunk for chunks in chunks_map.values() for chunk in chunks]
            self.chunk_titles = [f"Chunk {i+1}" for i in range(len(self.pdf_chunks))]
            self.upload_label.setText(f"✅ Loaded {len(files)} file(s) and {len(self.pdf_chunks)} chunks.")
            self.chunk_list.clear()
            for i, title in enumerate(self.chunk_titles):
                item = QListWidgetItem(title)
                item.setData(Qt.UserRole, i)
                self.chunk_list.addItem(item)
            self.progress.setVisible(False)


    def _chunk_tab_ui(self):
        tab = QWidget()
        layout = QHBoxLayout()
        layout.setSpacing(10)

        self.chunk_list = QListWidget()
        self.chunk_list.itemClicked.connect(self.show_chunk_text)
        self.chunk_list.setStyleSheet("""
            QListWidget {
                background-color: #f5f3ff;
                padding: 10px;
                border-radius: 8px;
            }
        """)
        layout.addWidget(self.chunk_list, 35)

        self.chunk_display = QTextEdit()
        self.chunk_display.setReadOnly(True)
        self.chunk_display.setStyleSheet("""
            QTextEdit {
                background-color: #ede9fe;
                padding: 15px;
                border-radius: 10px;
                font-size: 15px;
            }
        """)
        layout.addWidget(self.chunk_display, 65)

        tab.setLayout(layout)
        return tab

    def show_chunk_text(self, item):
        index = item.data(Qt.UserRole)
        self.chunk_display.setText(self.pdf_chunks[index])


    def _embedding_tab_ui(self):
        tab = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(15)

        self.embed_btn = QPushButton("🔄 Generate Embeddings and Push to Qdrant")
        self.embed_btn.clicked.connect(self.generate_embeddings)
        self.embed_btn.setStyleSheet("""
            background-color: #7c3aed;
            color: white;
            padding: 12px;
            font-weight: bold;
            border-radius: 10px;
        """)
        layout.addWidget(self.embed_btn)

        self.embed_status = QLabel("Ready")
        self.embed_status.setAlignment(Qt.AlignCenter)
        self.embed_status.setStyleSheet("font-size: 15px; color: #6b21a8;")
        layout.addWidget(self.embed_status)

        tab.setLayout(layout)
        return tab


    def generate_embeddings(self):
        if not self.pdf_chunks:
            self.embed_status.setText("⚠️ No chunks available.")
            return

        
        self.embeddings = generate_embeddings_for_chunks(self.pdf_chunks)
        self.embed_status.setText("✅ Embeddings generated and ready to preview/upload.")

        
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)

        for i, e in enumerate(self.embeddings[:5]):
            chunk_label = QLabel(f"📄 Chunk {i+1}:\n{e['text'][:250]}...")
            chunk_label.setStyleSheet("padding: 10px; background-color: #ede9fe; border-radius: 8px;")

            vector_label = QLabel(f"📐 Vector Dimension: {len(e['embedding'])}")
            vector_label.setStyleSheet("font-size: 13px; color: #5b21b6;")

            preview_vector = QLabel(f"🧠 Vector Preview: {e['embedding'][:10]}...")
            preview_vector.setStyleSheet("font-size: 13px; color: #4c1d95;")

            scroll_layout.addWidget(chunk_label)
            scroll_layout.addWidget(vector_label)
            scroll_layout.addWidget(preview_vector)
            scroll_layout.addSpacing(10)

        scroll_area.setWidget(scroll_content)
        self.tabs.widget(2).layout().addWidget(scroll_area)

        
        upload_btn = QPushButton("📤 Upload to Qdrant Now")
        upload_btn.setStyleSheet("""
            background-color: #16a34a;
            color: white;
            padding: 10px;
            border-radius: 8px;
            font-weight: bold;
        """)
        upload_btn.clicked.connect(lambda: self.upload_embeddings())
        self.tabs.widget(2).layout().addWidget(upload_btn)

    def upload_embeddings(self):
        if hasattr(self, 'embeddings') and self.embeddings:
            upload_embeddings_to_qdrant(self.embeddings)
            self.embed_status.setText("✅ Embeddings uploaded to Qdrant.")
        else:
            self.embed_status.setText("⚠️ No embeddings to upload.")


    
    def _summary_tab_ui(self):
        tab = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(15)

        self.summary_btn = QPushButton("📋 Summarize All Chunks")
        self.summary_btn.clicked.connect(self.generate_summary)
        self.summary_btn.setStyleSheet("""
            background-color: #6d28d9;
            color: white;
            padding: 12px;
            font-weight: bold;
            border-radius: 10px;
        """)
        layout.addWidget(self.summary_btn)

        self.summary_display = QTextEdit()
        self.summary_display.setReadOnly(True)
        self.summary_display.setStyleSheet("""
            QTextEdit {
                background-color: #faf5ff;
                padding: 15px;
                border-radius: 10px;
            }
        """)
        layout.addWidget(self.summary_display)

        tab.setLayout(layout)
        return tab

    def generate_summary(self):
        if not self.pdf_chunks:
            self.summary_display.setText("⚠️ No chunks to summarize.")
            return
        summary = summarize_chunks(self.pdf_chunks)
        self.summary_display.setText(summary)

    
    def _settings_tab_ui(self):
        tab = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(15)

        
        key_label = QLabel("🔐 OpenAI/Qdrant API Key:")
        key_label.setStyleSheet("font-weight: bold; color: #4c1d95; font-size: 15px;")
        layout.addWidget(key_label)

        self.api_input = QLineEdit()
        self.api_input.setEchoMode(QLineEdit.Password)
        self.api_input.setText(os.getenv("QDRANT_API_KEY", ""))
        self.api_input.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                border: 2px solid #c084fc;
                border-radius: 8px;
            }
        """)
        layout.addWidget(self.api_input)

        
        url_label = QLabel("🌐 Qdrant URL:")
        url_label.setStyleSheet("font-weight: bold; color: #4c1d95; font-size: 15px;")
        layout.addWidget(url_label)

        self.url_input = QLineEdit()
        self.url_input.setText(os.getenv("QDRANT_URL", "http://localhost:6333"))
        self.url_input.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                border: 2px solid #c084fc;
                border-radius: 8px;
            }
        """)
        layout.addWidget(self.url_input)

        
        collection_label = QLabel("📦 Collection Name:")
        collection_label.setStyleSheet("font-weight: bold; color: #4c1d95; font-size: 15px;")
        layout.addWidget(collection_label)

        self.collection_input = QLineEdit()
        self.collection_input.setText(os.getenv("COLLECTION_NAME", "pdf_chunks"))
        self.collection_input.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                border: 2px solid #c084fc;
                border-radius: 8px;
            }
        """)
        layout.addWidget(self.collection_input)

        
        save_btn = QPushButton("💾 Save Settings to .env")
        save_btn.clicked.connect(self.save_env_variables)
        save_btn.setStyleSheet("""
            background-color: #a855f7;
            color: white;
            padding: 10px;
            font-weight: bold;
            border-radius: 8px;
        """)
        layout.addWidget(save_btn)

        self.settings_status = QLabel("")
        self.settings_status.setStyleSheet("color: #6b21a8; font-size: 14px;")
        layout.addWidget(self.settings_status)

        tab.setLayout(layout)
        return tab

    def save_env_variables(self):
        api_key = self.api_input.text().strip()
        qdrant_url = self.url_input.text().strip()
        collection_name = self.collection_input.text().strip()

        if not api_key or not qdrant_url or not collection_name:
            self.settings_status.setText("⚠️ All fields must be filled!")
            return

        
        with open(".env", "w") as env_file:
            env_file.write(f"QDRANT_API_KEY={api_key}\n")
            env_file.write(f"QDRANT_URL={qdrant_url}\n")
            env_file.write(f"COLLECTION_NAME={collection_name}\n")

        self.settings_status.setText("✅ Settings saved to .env")

