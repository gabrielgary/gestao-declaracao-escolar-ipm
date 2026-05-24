import AuthGeneral from "../../../Components/Elements/Auth/AuthGeneral"
export default function AuthParent() {
    return (
        <>
            <AuthGeneral userType="encarregado" destination="/parent/dashboard" />
        </>
    )
}