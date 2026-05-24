import { useState, useEffect } from 'react'
import NavBarMenu from '../../../Components/Elements/NavBarMenu/NavBarMenu'
import DataTable from '../../../Components/Elements/DataTable/DataTable'
import Header from '../../../Components/Elements/Header/Header'
import '../../../assets/style/global.style.css'
import api from '../../../Services/api'
import Loading from '../../../Components/Elements/Loading/Loading'

const columns = [
    { label: "Nome do Funcionário", key: "name" },
    { label: "Código", key: "roll" },
    { label: "Email", key: "email" },
    { label: "Cargo", key: "class" },
    { label: "Estado", key: "status" },
];

export default function Funcionario() {
    const [searchTerm, setSearchTerm] = useState('')
    const [employees, setEmployees] = useState([])
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        const fetchEmployees = async () => {
            try {
                const response = await api.get('funcionarios/')
                const data = response.data.results || response.data
                setEmployees(data.map(emp => ({
                    id: emp.id_funcionario,
                    name: emp.nome_completo,
                    roll: emp.codigo_identificacao || 'N/A',
                    email: emp.email,
                    class: emp.cargo_nome || 'N/A',
                    img_path: emp.img_path,
                    status: emp.is_online ? 'online' : 'offline',
                    lastSeen: 'Há pouco tempo'
                })))
            } catch (error) {
                console.error("Erro ao carregar funcionários:", error)
            } finally {
                setLoading(false)
            }
        }
        fetchEmployees()
    }, [])

    const handleExport = async () => {
        try {
            const response = await api.get('funcionarios/export_csv/', {
                responseType: 'blob',
            });
            const url = window.URL.createObjectURL(new Blob([response.data]));
            const link = document.createElement('a');
            link.href = url;
            link.setAttribute('download', `funcionarios_${new Date().getTime()}.csv`);
            document.body.appendChild(link);
            link.click();
            link.remove();
        } catch (error) {
            console.error("Erro ao exportar funcionários:", error);
            alert("Erro ao gerar relatório. Por favor, tente novamente.");
        }
    };

    return (
        <div className="ContainerGeneral">
            <NavBarMenu />
            <main className="ContainerMain">
                <Header text1={"Recursos Humanos"} text2={"Funcionários"} onSearch={setSearchTerm} />
                {loading ? (
                    <div className="loading"><Loading /></div>
                ) : (
                    <DataTable
                        title="Lista de Funcionários"
                        externalSearchTerm={searchTerm}
                        data={employees}
                        columns={columns}
                        onAdd={handleExport}
                        searchPlaceholder="Pesquisar por nome ou ID"
                    />
                )}
            </main>
        </div>
    )
}

