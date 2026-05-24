import React, { useState } from 'react';
import styles from './BookCard.module.css';
import { IoEyeOutline } from 'react-icons/io5';
import { MdOutlineFileDownload } from 'react-icons/md';

function getInitials(title = '') {
  return title.split(' ').slice(0, 2).map(w => w[0] || '').join('').toUpperCase();
}

function svgDataUrl(title) {
  const initials = getInitials(title) || 'LB';
  const bg = '#f0fbf7';
  const fg = '#282831ff';
  const svg = `<svg xmlns='http://www.w3.org/2000/svg' width='600' height='800' viewBox='0 0 600 800'><rect width='100%' height='100%' fill='${bg}' rx='18'/><text x='50%' y='52%' dominant-baseline='middle' text-anchor='middle' font-family='Segoe UI, system-ui, Arial' font-size='140' fill='${fg}' font-weight='700'>${initials}</text></svg>`;
  return `data:image/svg+xml;utf8,${encodeURIComponent(svg)}`;
}

export default function BookCard({ book, onView, onAdd }) {
  const [loaded, setLoaded] = useState(false);
  const cover = book.cover || svgDataUrl(book.title);

  // Preload cover image to ensure it appears even if the <img> is delayed
  React.useEffect(() => {
    let cancelled = false;
    if (cover) {
      const img = new Image();
      img.src = cover;
      img.onload = () => { if (!cancelled) setLoaded(true); };
      img.onerror = () => { if (!cancelled) setLoaded(true); };
    }
    // fallback: if nothing loads in 3s, stop showing skeleton
    const t = setTimeout(() => { if (!cancelled) setLoaded(true); }, 3000);
    return () => { cancelled = true; clearTimeout(t); };
  }, [cover]);

  function handleImgError(e) {
    e.currentTarget.src = svgDataUrl(book.title);
    setLoaded(true);
  }

  return (
    <article className={styles.card} aria-label={`Livro ${book.title}`}>
      <div className={styles.cover}>
        {!loaded && <div className={styles.skeleton} aria-hidden />}

        <img 
          src={cover} 
          alt={`${book.title} capa`} 
          loading="lazy" 
          onLoad={() => setLoaded(true)} 
          onError={handleImgError} 
          className={styles.coverImage}
        />

        {book.recommended && <span className={styles.badge}>Recomendado</span>}
      </div>

      <div className={styles.info}>
        <h4 className={styles.title}>{book.title}</h4>
        <p className={styles.author}>{book.author}</p>
        <p className={styles.excerpt}>{book.excerpt || 'Resumo curto do livro para dar contexto ao leitor.'}</p>

        <div className={styles.footer}>
          <span className={styles.category}>{book.category}</span>
          <div className={styles.actions}>
            <button aria-label={`Ver ${book.title}`} className={styles.actionBtn} onClick={() => onView?.(book)}><IoEyeOutline size={18} /></button>
            <a href={book.caminho_arquivo} title='Baixar' aria-label={`Baixar ${book.title}`} className={styles.actionBtn} onClick={() => onAdd?.(book)}><MdOutlineFileDownload size={20} /></a>
          </div>
        </div>
      </div>
    </article>
  )
}
