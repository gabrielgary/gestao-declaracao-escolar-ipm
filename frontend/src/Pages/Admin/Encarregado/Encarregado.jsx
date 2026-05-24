import { useState, useEffect } from 'react'
import NavBarMenu from '../../../Components/Elements/NavBarMenu/NavBarMenu'
import DataTable from '../../../Components/Elements/DataTable/DataTable'
import Header from '../../../Components/Elements/Header/Header'
import '../../../assets/style/global.style.css'
import api from '../../../Services/api'
import Loading from '../../../Components/Elements/Loading/Loading'

const columns = [
    { label: "Nome do Encarregado", key: "name" },
    { label: "Email", key: "email" },
    { label: "Telefone", key: "phone" },
    { label: "Estado", key: "status" },
];

export default function Encarregado() {
    const [searchTerm, setSearchTerm] = useState('')
    const [guardians, setGuardians] = useState([])
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        const fetchGuardians = async () => {
            try {
                const response = await api.get('encarregados/')
                const data = response.data.results || response.data
                setGuardians(data.map(g => ({
                    id: g.id_encarregado,
                    name: g.nome_completo,
                    email: g.email || 'N/A',
                    phone: g.telefone ? (Array.isArray(g.telefone) ? g.telefone.join(', ') : g.telefone) : 'N/A',
                    img_path: g.img_path,
                    status: g.is_online ? 'online' : 'offline',
                    lastSeen: 'Disponível'
                })))
            } catch (error) {
                console.error("Erro ao carregar encarregados:", error)
            } finally {
                setLoading(false)
            }
        }
        fetchGuardians()
    }, [])

    const handleExport = async () => {
        try {
            const response = await api.get('encarregados/export_csv/', {
                responseType: 'blob',
            });
            const url = window.URL.createObjectURL(new Blob([response.data]));
            const link = document.createElement('a');
            link.href = url;
            link.setAttribute('download', `encarregados_${new Date().getTime()}.csv`);
            document.body.appendChild(link);
            link.click();
            link.remove();
        } catch (error) {
            console.error("Erro ao exportar encarregados:", error);
            alert("Erro ao gerar relatório. Por favor, tente novamente.");
        }
    };

    return (
        <div className="ContainerGeneral">
            <NavBarMenu />
            <main className="ContainerMain">
                <Header text1={"Administração"} text2={"Encarregados"} onSearch={setSearchTerm} />
                {loading ? (
                    <div className="loading"><Loading /></div>
                ) : (
                    <DataTable
                        title="Lista de Encarregados"
                        externalSearchTerm={searchTerm}
                        data={guardians}
                        columns={columns}
                        onAdd={handleExport}
                        searchPlaceholder="Pesquisar por nome ou ID"
                    />
                )}
            </main>
        </div>
    )
}

