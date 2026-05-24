import { useState, useEffect } from 'react'
import NavBarMenu from '../../../Components/Elements/NavBarMenu/NavBarMenu'
import DataTable from '../../../Components/Elements/DataTable/DataTable'
import Header from '../../../Components/Elements/Header/Header'
import '../../../assets/style/global.style.css'
import api from '../../../Services/api'
import Loading from '../../../Components/Elements/Loading/Loading'

const columns = [
    { label: "Nome do Estudante", key: "name" },
    { label: "Nº Matrícula", key: "roll" },
    { label: "Curso", key: "curso" },
    { label: "Turma", key: "class" },
    { label: "Email", key: "email" },
    { label: "Estado", key: "status" },
];

export default function Estudantes() {
    const [searchTerm, setSearchTerm] = useState('')
    const [students, setStudents] = useState([])
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        const fetchStudents = async () => {
            try {
                const response = await api.get('alunos/')
                const data = response.data.results || response.data
                setStudents(data.map(student => ({
                    id: student.id_aluno,
                    name: student.nome_completo,
                    roll: student.numero_matricula || 'N/A',
                    curso: student.curso_nome || 'N/A',
                    class: student.turma_codigo || 'N/A',
                    email: student.email,
                    img_path: student.img_path,
                    status: student.is_online ? 'online' : 'offline', // Using real online status from backend
                    lastSeen: 'Disponível'
                })))
            } catch (error) {
                console.error("Erro ao carregar estudantes:", error)
            } finally {
                setLoading(false)
            }
        }
        fetchStudents()
    }, [])

    const handleExport = async () => {
        try {
            const response = await api.get('alunos/export_csv/', {
                responseType: 'blob',
            });
            const url = window.URL.createObjectURL(new Blob([response.data]));
            const link = document.createElement('a');
            link.href = url;
            link.setAttribute('download', `alunos_${new Date().getTime()}.csv`);
            document.body.appendChild(link);
            link.click();
            link.remove();
        } catch (error) {
            console.error("Erro ao exportar alunos:", error);
            alert("Erro ao gerar relatório. Por favor, tente novamente.");
        }
    };

    return (
        <div className="ContainerGeneral">
            <NavBarMenu />
            <main className="ContainerMain">
                <Header text1={"Administração"} text2={"Estudantes"} onSearch={setSearchTerm} />
                {loading ? (
                    <div className="loading"><Loading /></div>
                ) : (
                    <DataTable
                        title="Lista de Estudantes"
                        externalSearchTerm={searchTerm}
                        data={students}
                        columns={columns}
                        onAdd={handleExport}
                        searchPlaceholder="Pesquisar por nome ou matrícula"
                    />
                )}
            </main>
        </div>
    )
}

