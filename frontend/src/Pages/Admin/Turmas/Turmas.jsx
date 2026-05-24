import { useState, useEffect } from 'react'
import NavBarMenu from '../../../Components/Elements/NavBarMenu/NavBarMenu'
import DataTable from '../../../Components/Elements/DataTable/DataTable'
import Header from '../../../Components/Elements/Header/Header'
import '../../../assets/style/global.style.css'
import api from '../../../Services/api'
import TurmaModal from './TurmaModal'
import Loading from '../../../Components/Elements/Loading/Loading'

const columns = [
    { label: "Código", key: "codigo_turma" },
    { label: "Curso", key: "curso_nome" },
    { label: "Classe", key: "classe_nivel" },
    { label: "Período", key: "periodo_nome" },
    { label: "Ano", key: "ano" },
    { label: "Sala", key: "sala_numero" },
    { label: "Coordenador", key: "responsavel_nome" },
];

export default function Turmas() {
    const [searchTerm, setSearchTerm] = useState('')
    const [turmas, setTurmas] = useState([])
    const [loading, setLoading] = useState(true)

    const [showModal, setShowModal] = useState(false);

    const fetchTurmas = async () => {
        setLoading(true);
        try {
            const response = await api.get('turmas/')
            const data = response.data.results || response.data
            setTurmas(data)
        } catch (error) {
            console.error("Erro ao carregar turmas:", error)
        } finally {
            setLoading(false)
        }
    }

    useEffect(() => {
        fetchTurmas()
    }, [])

    const handleAdd = () => {
        setShowModal(true);
    };

    const handleSuccess = () => {
        fetchTurmas();
    };

    /* const handleEdit = (item) => {
        console.log("Edit turma:", item);
    };

    const handleDelete = (item) => {
        console.log("Delete turma:", item);
    };
    */
    return (
        <div className="ContainerGeneral">
            <NavBarMenu />
            <main className="ContainerMain">
                <Header text1={"Acadêmico"} text2={"Gestão de Turmas"} onSearch={setSearchTerm} />
                {loading ? (
                    <div className="loading"><Loading/></div>
                ) : (
                    <DataTable
                        title="Listagem de Turmas"
                        externalSearchTerm={searchTerm}
                        data={turmas}
                        columns={columns}
                        onAdd={false}
                        addButtonLabel="Criar_Turma"
                        /* onEdit={handleEdit}
                          onDelete={handleDelete}*/
                        searchPlaceholder="Pesquisar por código ou curso..."
                    />
                )}
                {showModal && (
                    <TurmaModal
                        onClose={() => setShowModal(false)}
                        onSuccess={handleSuccess}
                    />
                )}
            </main>
        </div>
    )
}
