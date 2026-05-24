import AuthGeneral from "../../../Components/Elements/Auth/AuthGeneral"

export default function AuthAdmin() {
    return (
        <>
            <AuthGeneral userType="funcionario" destination="/admin/dashboard" />
        </>
    )
}