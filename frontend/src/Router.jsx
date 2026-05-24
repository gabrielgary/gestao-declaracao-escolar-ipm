import { Route, Routes } from 'react-router-dom'
// importing of views for routers
import MainSite from './Pages/Public/Site/MainSite'
import Dashboards from './Pages/Admin/Dashboards/Dashboards'
import AuthParent from './Pages/Client/Parents/AuthParent'
import AuthStudent from './Pages/Client/Students/AuthStudent'
import AuthAdmin from './Pages/Admin/Auth/AuthAdmin'
import LIbrary from './Pages/Public/LIbrary/LIbrary'
// estudantes
import DashboardsStudents from './Pages/Client/Students/Dashboards/DashboardsStudents'
import DocumentsCliente from './Pages/Client/Students/DocumentsCliente/DocumentsCliente'
import AskStudent from './Pages/Client/Students/AskStudent/AskStudent'
import Grades from './Pages/Client/Students/Grades/Grades'
import Schedule from './Pages/Client/Students/Schedule/Schedule'
import Attendance from './Pages/Client/Students/Attendance/Attendance'
import Settings from './Pages/Admin/Settings/Settings'
import Accounts from './Pages/Admin/Accounts/Accounts'
import Histories from './Pages/Admin/Histories/Histories'
// parent
import Children from './Pages/Client/Parents/Children/Children'
import ChildrenActions from './Pages/Client/Parents/ChildrenActions/ChildrenActions'
import DashboardEncarregado from './Pages/Client/Parents/Dashboards/DashboardEncarregado'
import Documentos from './Pages/Client/Parents/Documentos/Documentos'
import SolicitacaoParent from './Pages/Client/Parents/SolicitacaoParent/SolicitacaoParent'
//import Asks from './Pages/Admin'
import Encarregado from './Pages/Admin/Encarregado/Encarregado'
import Estudantes from './Pages/Admin/Estudantes/Estudantes'
import Funcionario from './Pages/Admin/Funcionario/Funcionario'
import Solicitacao from './Pages/Admin/Solicitacao/Solicitacao'
import Turmas from './Pages/Admin/Turmas/Turmas'
import LibraryAdmin from './Pages/Admin/Library/Library'
// documents
import Certificado from './Pages/Admin/Certificado/Certificado'
import Boletim from './Pages/Admin/Boletim/Boletim'
import Declaracao from './Pages/Admin/Declaracao/Declaracao'
import YasminChat from './Pages/YasminAI/YasminChat'
import GradeLaunching from './Pages/Admin/Grades/GradeLaunching'
import Reports from './Pages/Admin/Reports/Reports'

import ProtectedRoute from './Components/Security/ProtectedRoute'
import Profile from './Pages/Common/Profile/Profile';
import NotFound from './Pages/Public/NotFound/NotFound';
import VerificarDocumento from './Pages/Public/VerificarDocumento/VerificarDocumento';
import ForgotPassword from './Pages/Common/Auth/ForgotPassword';
import ResetPassword from './Pages/Common/Auth/ResetPassword';

const Routers = () => {
    return (
        <Routes>
            {/***ADMINSTRADOR** */}
            <Route path='/admin/dashboard' element={<ProtectedRoute allowedTypes={['funcionario']}><Dashboards /></ProtectedRoute>}></Route>
            <Route path='/admin/' element={<ProtectedRoute allowedTypes={['funcionario']}><Dashboards /></ProtectedRoute>}></Route>
            <Route path='/admin/funcionario' element={<ProtectedRoute allowedTypes={['funcionario']}><Funcionario /></ProtectedRoute>}></Route>
            <Route path='/admin/student' element={<ProtectedRoute allowedTypes={['funcionario']}><Estudantes /></ProtectedRoute>}></Route>
            <Route path='/admin/parent' element={<ProtectedRoute allowedTypes={['funcionario']}><Encarregado /></ProtectedRoute>}></Route>
            <Route path='/admin/declaracao' element={<ProtectedRoute allowedTypes={['funcionario']}><Declaracao /></ProtectedRoute>}></Route>
            <Route path='/admin/certificado' element={<ProtectedRoute allowedTypes={['funcionario']}><Certificado /></ProtectedRoute>}></Route>
            <Route path='/admin/boletim' element={<ProtectedRoute allowedTypes={['funcionario']}><Boletim /></ProtectedRoute>}></Route>
            <Route path='/admin/ask' element={<ProtectedRoute allowedTypes={['funcionario']}><Solicitacao /></ProtectedRoute>}></Route>
            <Route path='/admin/turmas' element={<ProtectedRoute allowedTypes={['funcionario']}><Turmas /></ProtectedRoute>}></Route>
            <Route path='/admin/library' element={<ProtectedRoute allowedTypes={['funcionario']}><LibraryAdmin /></ProtectedRoute>}></Route>
            <Route path='/admin/history' element={<ProtectedRoute allowedTypes={['funcionario']}><Histories /></ProtectedRoute>}></Route>
            <Route path='/admin/setting' element={<ProtectedRoute allowedTypes={['funcionario']}><Settings /></ProtectedRoute>}></Route>
            <Route path='/admin/notas' element={<ProtectedRoute allowedTypes={['funcionario']}><GradeLaunching /></ProtectedRoute>}></Route>
            <Route path='/admin/reports' element={<ProtectedRoute allowedTypes={['funcionario']}><Reports /></ProtectedRoute>}></Route>
            <Route path='/admin/auth' element={<AuthAdmin />}></Route>
            <Route path='/agent/account' element={<ProtectedRoute allowedTypes={['funcionario']}><Accounts /></ProtectedRoute>}></Route>
            <Route path='/admin/yasmin' element={<ProtectedRoute allowedTypes={['funcionario']}><YasminChat /></ProtectedRoute>}></Route>
            <Route path='/agent/yasmin' element={<ProtectedRoute allowedTypes={['funcionario']}><YasminChat /></ProtectedRoute>}></Route>

            {/***ALUNO** */}
            <Route path='/student/dashboard' element={<ProtectedRoute allowedTypes={['aluno']}><DashboardsStudents /></ProtectedRoute>}></Route>
            <Route path='/student/document' element={<ProtectedRoute allowedTypes={['aluno']}><DocumentsCliente /></ProtectedRoute>}></Route>
            <Route path='/student/ask' element={<ProtectedRoute allowedTypes={['aluno']}><AskStudent /></ProtectedRoute>}></Route>
            <Route path='/student/grades' element={<ProtectedRoute allowedTypes={['aluno']}><Grades /></ProtectedRoute>}></Route>
            <Route path='/student/schedule' element={<ProtectedRoute allowedTypes={['aluno']}><Schedule /></ProtectedRoute>}></Route>
            <Route path='/student/attendance' element={<ProtectedRoute allowedTypes={['aluno']}><Attendance /></ProtectedRoute>}></Route>
            <Route path='/student/auth' element={<AuthStudent />}></Route>
            <Route path='/student/yasmin' element={<ProtectedRoute allowedTypes={['aluno']}><YasminChat /></ProtectedRoute>}></Route>

            {/***ENCARREGADO** */}
            <Route path='/parent/dashboard' element={<ProtectedRoute allowedTypes={['encarregado']}><DashboardEncarregado /></ProtectedRoute>}></Route>
            <Route path='/parent/children' element={<ProtectedRoute allowedTypes={['encarregado']}><Children /></ProtectedRoute>}></Route>
            <Route path='/parent/ask' element={<ProtectedRoute allowedTypes={['encarregado']}><SolicitacaoParent /></ProtectedRoute>}></Route>
            <Route path='/parent/document' element={<ProtectedRoute allowedTypes={['encarregado']}><Documentos /></ProtectedRoute>}></Route>
            <Route path='/parent/actionstudent' element={<ProtectedRoute allowedTypes={['encarregado']}><ChildrenActions /></ProtectedRoute>}></Route>
            <Route path='/parent/auth' element={<AuthParent />}></Route>
            <Route path='/parent/yasmin' element={<ProtectedRoute allowedTypes={['encarregado']}><YasminChat /></ProtectedRoute>}></Route>

            {/*** RECUPERAÇÃO DE SENHA ***/}
            <Route path='/auth/forgot-password' element={<ForgotPassword />}></Route>
            <Route path='/auth/reset-password' element={<ResetPassword />}></Route>

            {/*** COMUM ***/}
            <Route path='/profile' element={<ProtectedRoute><Profile /></ProtectedRoute>}></Route>

            {/***PUBLICO** */}{/* */}
            <Route path='/' index element={<MainSite />}></Route>{/* */}
            <Route path='/public/site' element={<MainSite />}></Route>{/* */}
            <Route path='/public/library' element={<LIbrary />}></Route>{/* */}
            <Route path='/public/library/buy' element={"/public/library/buy"}></Route>{/* */}
            <Route path='/public/verificar' element={<VerificarDocumento />}></Route>
            <Route path='/public/verificar/:uuid' element={<VerificarDocumento />}></Route>

            {/* Rota 404 - Not Found */}
            <Route path='*' element={<NotFound />}></Route>
        </Routes>
    )
}

export default Routers