import os
from typing import List, Dict
from fastapi import UploadFile
import pytesseract
from pdf2image import convert_from_path
from PIL import Image
import chromadb
from sentence_transformers import SentenceTransformer
import numpy as np
import tempfile
import shutil

class DocumentProcessor:
    def __init__(self):
        self.embeddings_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.chroma_client = chromadb.Client()
        self.collection = self.chroma_client.create_collection(name="study_notes")
        self.temp_dir = tempfile.mkdtemp()

    async def process_document(self, file: UploadFile) -> List[str]:
        """Process uploaded document and extract topics"""
        try:
            # Save uploaded file temporarily
            temp_path = os.path.join(self.temp_dir, file.filename)
            with open(temp_path, "wb") as buffer:
                content = await file.read()
                buffer.write(content)

            # Process based on file type
            if file.filename.lower().endswith('.pdf'):
                text = await self._process_pdf(temp_path)
            elif file.filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                text = await self._process_image(temp_path)
            else:
                text = await self._process_text(temp_path)

            # Extract topics and store in vector database
            topics = await self._extract_topics(text)
            await self._store_document(text, topics)

            # Cleanup
            os.remove(temp_path)
            return topics

        except Exception as e:
            raise Exception(f"Error processing document: {str(e)}")

    async def _process_pdf(self, file_path: str) -> str:
        """Extract text from PDF using OCR"""
        try:
            # Convert PDF to images
            images = convert_from_path(file_path)
            text = ""
            
            # Process each page
            for image in images:
                text += pytesseract.image_to_string(image)
            
            return text
        except Exception as e:
            raise Exception(f"Error processing PDF: {str(e)}")

    async def _process_image(self, file_path: str) -> str:
        """Extract text from image using OCR"""
        try:
            image = Image.open(file_path)
            text = pytesseract.image_to_string(image)
            return text
        except Exception as e:
            raise Exception(f"Error processing image: {str(e)}")

    async def _process_text(self, file_path: str) -> str:
        """Process plain text file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            raise Exception(f"Error processing text file: {str(e)}")

    async def _extract_topics(self, text: str) -> List[str]:
        """Extract main topics from the text using the LLM"""
        # Split text into chunks
        chunks = self._split_text(text)
        
        # Generate embeddings for chunks
        embeddings = self.embeddings_model.encode(chunks)
        
        # Use clustering to identify main topics
        from sklearn.cluster import KMeans
        n_clusters = min(5, len(chunks))  # Limit to 5 topics or less
        kmeans = KMeans(n_clusters=n_clusters)
        clusters = kmeans.fit_predict(embeddings)
        
        # Extract representative chunks for each cluster
        topics = []
        for i in range(n_clusters):
            cluster_chunks = [chunks[j] for j in range(len(chunks)) if clusters[j] == i]
            # Use the chunk closest to cluster center as topic
            center = kmeans.cluster_centers_[i]
            distances = [np.linalg.norm(embeddings[j] - center) for j in range(len(chunks)) if clusters[j] == i]
            topic_idx = np.argmin(distances)
            topics.append(cluster_chunks[topic_idx][:100])  # Take first 100 chars as topic
        
        return topics

    async def _store_document(self, text: str, topics: List[str]):
        """Store document in vector database"""
        # Split text into chunks
        chunks = self._split_text(text)
        
        # Generate embeddings
        embeddings = self.embeddings_model.encode(chunks)
        
        # Store in ChromaDB
        self.collection.add(
            embeddings=embeddings.tolist(),
            documents=chunks,
            metadatas=[{"topics": topics} for _ in chunks]
        )

    def _split_text(self, text: str, chunk_size: int = 1000) -> List[str]:
        """Split text into overlapping chunks"""
        chunks = []
        start = 0
        while start < len(text):
            end = start + chunk_size
            if end > len(text):
                end = len(text)
            chunks.append(text[start:end])
            start = end - 200  # 200 character overlap
        return chunks

    async def get_relevant_context(self, topic: str) -> str:
        """Retrieve relevant context for a given topic"""
        # Generate embedding for the topic
        topic_embedding = self.embeddings_model.encode([topic])[0]
        
        # Query ChromaDB
        results = self.collection.query(
            query_embeddings=[topic_embedding.tolist()],
            n_results=3
        )
        
        # Combine relevant chunks
        context = " ".join(results['documents'][0])
        return context

    def __del__(self):
        """Cleanup temporary directory"""
        try:
            shutil.rmtree(self.temp_dir)
        except:
            pass 