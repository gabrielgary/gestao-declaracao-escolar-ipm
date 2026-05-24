import React from 'react';
import style from './DocumentPreviewModal.module.css';
import { IoClose, IoDownload } from 'react-icons/io5';

const DocumentPreviewModal = ({ isOpen, onClose, pdfUrl, title }) => {
    if (!isOpen) return null;

    const handleDownload = () => {
        const link = document.createElement('a');
        link.href = pdfUrl;
        link.download = title || 'documento.pdf';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    };

    return (
        <div className={style.Overlay} onClick={onClose}>
            <div className={style.Modal} onClick={(e) => e.stopPropagation()}>
                <div className={style.Header}>
                    <h3>{title || 'Visualizar Documento'}</h3>
                    <div className={style.Actions}>
                        <button
                            className={style.DownloadBtn}
                            onClick={handleDownload}
                            title="Baixar Documento"
                        >
                            <IoDownload /> Baixar
                        </button>
                        <button
                            className={style.CloseBtn}
                            onClick={onClose}
                            title="Fechar"
                        >
                            <IoClose />
                        </button>
                    </div>
                </div>
                <div className={style.Content}>
                    {pdfUrl ? (
                        <iframe
                            src={`${pdfUrl}#toolbar=0`}
                            title="Pré-visualização do documento"
                            width="100%"
                            height="100%"
                        />
                    ) : (
                        <div className={style.NoContent}>
                            Documento não disponível para visualização.
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default DocumentPreviewModal;
