import AuthGeneral from "../../../Components/Elements/Auth/AuthGeneral"
export default function AuthStudent() {
    return (
        <>
            <AuthGeneral userType="aluno" destination="/student/dashboard" />
        </>
    )
}