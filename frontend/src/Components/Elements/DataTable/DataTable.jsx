import { useState } from 'react';
import style from './DataTable.module.css';
import { FaMagnifyingGlass, FaPencil, FaTrash } from 'react-icons/fa6';
import { IoFilterSharp } from 'react-icons/io5';

export default function DataTable({
    title = "Students List",
    data = [],
    columns = [],
    onAdd,
    //onEdit,
    //onDelete,
    searchPlaceholder = "Search by name or roll",
    externalSearchTerm = "",
    loading = false,
    addButtonLabel
}) {
    const [searchTerm, setSearchTerm] = useState('');
    const [currentPage, setCurrentPage] = useState(1);
    const [itemsPerPage] = useState(10);
    const [filterDays, setFilterDays] = useState(30);

    const activeSearchTerm = externalSearchTerm || searchTerm;

    // Filter data based on search term
    const filteredData = data.filter(item => {
        const searchLower = activeSearchTerm.toLowerCase();
        return columns.some(col => {
            const value = item[col.key];
            return value && value.toString().toLowerCase().includes(searchLower);
        });
    });

    // Pagination logic
    const indexOfLastItem = currentPage * itemsPerPage;
    const indexOfFirstItem = indexOfLastItem - itemsPerPage;
    const currentItems = filteredData.slice(indexOfFirstItem, indexOfLastItem);
    const totalPages = Math.ceil(filteredData.length / itemsPerPage);

    const handlePageChange = (pageNumber) => {
        setCurrentPage(pageNumber);
    };

    return (
        <div className={style.DataTableContainer}>
            <div className={style.TableHeader}>
                <div className={style.TitleSection}>
                    <h2>{title}</h2>
                  
                </div>
                {onAdd && (
                    <button className={style.AddButton} onClick={onAdd}>
                        {
                            
                        addButtonLabel || `Exportar ${title.split(' ')[2] || 'Item'}`}
                    </button>
                )}
            </div>

            <div className={style.TableCard}>
                <div className={style.TableControls}>
                    <div className={style.ControlsRight}>
                        <div className={style.SearchBox}>
                            <FaMagnifyingGlass />
                            <input
                                type="text"
                                placeholder={searchPlaceholder}
                                value={activeSearchTerm}
                                onChange={(e) => setSearchTerm(e.target.value)}
                            />
                        </div>
                        <div className={style.FilterDropdown}>
                            <IoFilterSharp />
                            <select value={filterDays} onChange={(e) => setFilterDays(e.target.value)}>
                                <option value={7}>Last 7 days</option>
                                <option value={30}>Last 30 days</option>
                                <option value={90}>Last 90 days</option>
                            </select>
                        </div>
                    </div>
                </div>

                <div className={style.TableWrapper}>
                    <table className={style.Table}>
                        <thead>
                            <tr>
                                <th>

                                </th>
                                {columns.map((col, index) => (
                                    <th key={index}>{col.label}</th>
                                ))}
                                {/*(onEdit || onDelete) && <th>Action</th>*/}
                            </tr>
                        </thead>
                        <tbody>
                            {loading ? (
                                <tr>
                                    <td colSpan={columns.length + 2} className={style.LoadingState}>
                                        <div className={style.LoadingWrapper}>
                                            <div className={style.Spinner}></div>
                                            <span>Carregando dados...</span>
                                        </div>
                                    </td>
                                </tr>
                            ) : currentItems.length > 0 ? (
                                currentItems.map((item, index) => (
                                    <tr key={index}>
                                        <td>

                                        </td>
                                        {columns.map((col, colIndex) => (
                                            <td key={colIndex}>
                                                {col.key === 'name' && (item.avatar || item.img_path) ? (
                                                    <div className={style.NameCell}>
                                                        <img src={item.avatar || item.img_path} alt={item[col.key]} />
                                                        <span>{item[col.key]}</span>
                                                    </div>
                                                ) : col.key === 'name' && item.initials ? (
                                                    <div className={style.NameCell}>
                                                        <div className={style.Avatar}>{item.initials}</div>
                                                        <span>{item[col.key]}</span>
                                                    </div>
                                                ) : col.key === 'status' ? (
                                                    <div className={style.StatusWrapper}>
                                                        <span className={`${style.StatusDot} ${item.status === 'online' ? style.Online : style.Offline}`}></span>
                                                        <span className={style.StatusText}>
                                                            {item.status === 'online' ? 'Online' : 'Offline'}
                                                        </span>
                                                        <div className={style.StatusTooltip}>
                                                            {item.status === 'online' ? 'Online desde: ' : 'Visto por último: '}
                                                            {item.lastSeen || 'N/A'}
                                                        </div>
                                                    </div>
                                                ) : (
                                                    item[col.key]
                                                )}
                                            </td>
                                        ))}
                                        {/*(onEdit || onDelete) ? (
                                            <td>
                                                <div className={style.ActionButtons}>
                                                    {onEdit && (
                                                        <button
                                                            className={style.EditBtn}
                                                            onClick={() => onEdit(item)}
                                                            title="Edit"
                                                        >
                                                            <FaPencil />
                                                        </button>
                                                    )}
                                                    {onDelete && (
                                                        <button
                                                            className={style.DeleteBtn}
                                                            onClick={() => onDelete(item)}
                                                            title="Delete"
                                                        >
                                                            <FaTrash />
                                                        </button>
                                                    )}
                                                </div>
                                            </td>
                                        ) : null*/}
                                    </tr>
                                ))
                            ) : (
                                <tr>
                                    <td colSpan={columns.length + 2} className={style.EmptyState}>
                                        Sem Dados Encontrados
                                    </td>
                                </tr>
                            )}
                        </tbody>
                    </table>
                </div>

                <div className={style.TableFooter}>
                    <div className={style.Pagination}>
                        <button
                            onClick={() => handlePageChange(currentPage - 1)}
                            disabled={currentPage === 1}
                            className={style.PageArrow}
                        >
                            ‹
                        </button>

                        {[...Array(Math.min(5, totalPages))].map((_, index) => {
                            let pageNumber;
                            if (totalPages <= 5) {
                                pageNumber = index + 1;
                            } else if (currentPage <= 3) {
                                pageNumber = index + 1;
                            } else if (currentPage >= totalPages - 2) {
                                pageNumber = totalPages - 4 + index;
                            } else {
                                pageNumber = currentPage - 2 + index;
                            }

                            return (
                                <button
                                    key={index}
                                    onClick={() => handlePageChange(pageNumber)}
                                    className={currentPage === pageNumber ? style.ActivePage : ''}
                                >
                                    {pageNumber}
                                </button>
                            );
                        })}

                        {totalPages > 5 && (
                            <>
                                <span className={style.Ellipsis}>...</span>
                                <button onClick={() => handlePageChange(totalPages)}>
                                    {totalPages}
                                </button>
                            </>
                        )}

                        <button
                            onClick={() => handlePageChange(currentPage + 1)}
                            disabled={currentPage === totalPages}
                            className={style.PageArrow}
                        >
                            ›
                        </button>
                    </div>

                    <div className={style.PerPageSelector}>
                        <span>{itemsPerPage} Itens por Página</span>
                    </div>
                </div>
            </div>
        </div>
    );
}
