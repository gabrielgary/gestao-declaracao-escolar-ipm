import { Link } from "react-router-dom";
import { MdBook, MdDownload, MdChevronRight } from "react-icons/md";
import { FaEye, FaDownload, FaBook, FaCartPlus } from 'react-icons/fa6'
import MenuSitePublic from "../../../Components/Utils/MenuSitePublic/MenuSitePublic";
import SearchBar from "../../../Components/Utils/SearchBar/SearchBar";
import BookCard from "../../../Components/Utils/BookCard/BookCard";
import style from './LIbrary.module.css';
import { useState, useMemo, useEffect } from "react";
import AuroraBackground from "../Site/AuroraBackground";
//import api from "../../../Services/api"; // Removed to avoid token issues
import axios from 'axios';

// Instance for public requests without Auth Token
const API_BASE = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1' 
  ? 'http://127.0.0.1:8000/api/v1/' 
  : 'https://gestao-declaracao-escolar-ipm.onrender.com/api/v1/';

const MEDIA_BASE = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
  ? 'http://127.0.0.1:8000/media'
  : 'https://gestao-declaracao-escolar-ipm.onrender.com/media';

const publicApi = axios.create({
  baseURL: API_BASE,
});

const BASE_URL_MEDIA = MEDIA_BASE;

const normalizeUrl = (url) => {
  if (!url) return null;
  if (url.startsWith('http')) return url;

  // Ensure we don't double up /media if it's already there
  const cleanPath = url.startsWith('/media/') ? url.replace('/media/', '') : (url.startsWith('media/') ? url.replace('media/', '') : url);

  return `${BASE_URL_MEDIA}${cleanPath.startsWith('/') ? '' : '/'}${cleanPath}`;
};

export default function LIbrary() {
  const [category, setCategory] = useState({ id: 'Todas', nome: 'Todas' });
  const [books, setBooks] = useState([]);
  const [categories, setCategories] = useState([{ id: 'Todas', nome: 'Todas' }]);
  const [loading, setLoading] = useState(true);
  const [selectedBook, setSelectedBook] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [booksRes, catsRes] = await Promise.all([
          publicApi.get('/livros/'),
          publicApi.get('/categorias/')
        ]);

        setBooks(booksRes.data.results || booksRes.data);

        const backendCats = catsRes.data.results || catsRes.data;
        setCategories([
          { id: 'Todas', nome: 'Todas' },
          ...backendCats.map(c => ({ id: c.id_categoria, nome: c.nome_categoria }))
        ]);
      } catch (error) {
        console.error("Erro ao carregar dados da biblioteca:", error);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  const recommended = useMemo(() => books.filter(b => b.recomendado), [books]);

  const filtered = useMemo(() => {
    let result = books;
    if (category.id !== 'Todas') {
      result = result.filter(b => b.categoria_nome === category.nome);
    }
    if (searchTerm.trim()) {
      result = result.filter(b =>
        b.titulo.toLowerCase().includes(searchTerm.toLowerCase()) ||
        (b.editora && b.editora.toLowerCase().includes(searchTerm.toLowerCase()))
      );
    }
    return result;
  }, [books, category, searchTerm]);

  function handleView(book) {
    if (book.caminho_arquivo) {
      setSelectedBook(book);
    }
  }

  function handleAdd(book) {
    if (book.caminho_arquivo) {
      const link = document.createElement('a');
      link.href = book.caminho_arquivo;
      link.download = `${book.titulo}.pdf`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    }
  }

  // Helper function to map backend book to BookCard props
  const mapBook = (b) => ({
    id: b.id_livro,
    title: b.titulo,
    author: b.editora || 'Editora não informada',
    category: b.categoria_nome,
    recommended: b.recomendado,
    cover: normalizeUrl(b.img_path),
    pdf: normalizeUrl(b.caminho_arquivo),
    caminho_arquivo: normalizeUrl(b.caminho_arquivo),
    excerpt: b.excerpt || 'Resumo não disponível.'
  });

  return (
    <AuroraBackground>
      <main className={style.body}>
        <MenuSitePublic />

        <div className="relative z-10 w-full flex flex-col">
          {/* Recommended Books - Full Width */}
          <section className={style.recommendedBooks}>
            <SearchBar
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />

            <div className={style.sectionHeader}>
              <h3>Livros Recomendados</h3>
            </div>
            <div className={style.listEBooksRecommendedBooks}>
              <div className={style.resourceGrid}>
                {loading ? (
                  Array.from({ length: 6 }).map((_, i) => (
                    <div key={i} className={style.skeletonCard}>
                      <div className={style.skeletonCover}></div>
                      <div className={style.skeletonInfo}>
                        <div className={style.skeletonTitle}></div>
                        <div className={style.skeletonAuthor}></div>
                        <div className={style.skeletonExcerpt}></div>
                      </div>
                    </div>
                  ))
                ) : recommended.length > 0 ? (
                  recommended.map(book => (
                    <BookCard key={book.id_livro} book={mapBook(book)} onView={handleView} onAdd={handleAdd} />
                  ))
                ) : (
                  <div className={style.emptyStateStrip}>
                    <FaBook size={40} className="mb-4 opacity-20" />
                    <p>Nenhum livro recomendado no momento.</p>
                  </div>
                )}
              </div>
            </div>
          </section>

          {/* Categories - Centered */}
          <div className="px-4 sm:px-6 lg:px-8 max-w-[1440px] mx-auto w-full pb-10">
            <section className={style.BooksByCategory}>
              <div>
                <h3>Categorias</h3>
                <div className={style.containerCategory}>
                  {categories.map(cat => (
                    <button
                      key={cat.id}
                      onClick={() => setCategory(cat)}
                      className={`${cat.id === category.id ? style.is_selected : ''}`}
                    >
                      {cat.nome}
                    </button>
                  ))}
                </div>

                <div className={style.listEBooks}>
                  {loading ? (
                    Array.from({ length: 8 }).map((_, i) => (
                      <div key={i} className={style.skeletonCard}>
                        <div className={style.skeletonCover}></div>
                        <div className={style.skeletonInfo}>
                          <div className={style.skeletonTitle}></div>
                          <div className={style.skeletonAuthor}></div>
                          <div className={style.skeletonExcerpt}></div>
                        </div>
                      </div>
                    ))
                  ) : filtered.length > 0 ? (
                    filtered.map(book => (
                      <BookCard key={book.id_livro} book={mapBook(book)} onView={handleView} onAdd={handleAdd} />
                    ))
                  ) : (
                    <div className={style.emptyStateGrid}>
                      <FaBook size={60} className="mb-4 opacity-10" />
                      <p>Nenhum livro encontrado nesta categoria.</p>
                      <span>Tente buscar por outro termo ou selecione outra categoria.</span>
                    </div>
                  )}
                </div>
              </div>
            </section>
          </div>
        </div>

        {/* Modal Viewer */}
        {selectedBook && (
          <div className={style.modalOverlay} onClick={() => setSelectedBook(null)}>
            <div className={style.modalContent} onClick={e => e.stopPropagation()}>
              <div className={style.modalHeader}>
                <h3>{selectedBook.title || selectedBook.titulo}</h3>
                <button onClick={() => setSelectedBook(null)} className={style.closeBtn}>×</button>
              </div>
              <div className={style.modalBody}>
                {selectedBook.pdf ? (
                  <iframe
                    src={`${selectedBook.pdf}#toolbar=0&navpanes=0&scrollbar=1`}
                    title="Leitor de PDF"
                    className={style.pdfViewer}
                  ></iframe>
                ) : (
                  <div className={style.errorPlaceholder}>
                    Documento não disponível para visualização.
                  </div>
                )}
              </div>
              <div className={style.modalFooter}>
                <button
                  className={style.downloadBtn}
                  onClick={() => handleAdd(selectedBook)}
                >
                  <MdDownload size={20} style={{ marginRight: '8px' }} /> Baixar PDF
                </button>
              </div>
            </div>
          </div>
        )}
      </main>
    </AuroraBackground>
  )
}
