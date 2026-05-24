import React, { useState } from 'react';
import style from './Profile.module.css';
import '../../../assets/style/global.style.css';
import MenuNavBarCliente from '../../../Components/Elements/MenuNavBarCliente/MenuNavBarCliente';
import NavBarMenu from '../../../Components/Elements/NavBarMenu/NavBarMenu';
import Header from '../../../Components/Elements/Header/Header';
import { useAuth } from '../../../Context/AuthContext';
import api from '../../../Services/api';
import { RiUserLine, RiLockLine, RiMailLine, RiPhoneLine, RiMapPinLine, RiImageEditLine, RiSaveLine } from 'react-icons/ri';

const Profile = () => {
    const { user } = useAuth();
    const [loading, setLoading] = useState(false);
    const [passwordData, setPasswordData] = useState({
        currentPassword: '',
        newPassword: '',
        confirmPassword: ''
    });
    const [previewImage, setPreviewImage] = useState(null);
    const [rawImage, setRawImage] = useState(null);
    const [passwordVerified, setPasswordVerified] = useState(false);

    // Sidebar choice based on user type
    const Sidebar = user?.tipo === 'funcionario' ? NavBarMenu : user?.tipo==="aluno"? MenuNavBarCliente:MenuNavBarCliente;

    const sidebarProp = user?.tipo === 'funcionario' ? {} : { user: user?.tipo === 'aluno' ? 'student' : user?.tipo };

    const handleImageChange = (e) => {
        const file = e.target.files[0];
        if (file) {
            setRawImage(file);
            setPreviewImage(URL.createObjectURL(file));
        }
    };

    const handleUpdatePhoto = async () => {
        if (!rawImage) return;
        setLoading(true);
        const formData = new FormData();
        formData.append('img_path', rawImage);

        try {
            // Usar o endpoint específico de update profile que lida com o token automaticamente
            await api.post('/auth/update-profile/', formData, {
                headers: { 'Content-Type': 'multipart/form-data' }
            });
            alert("Foto de perfil atualizada com sucesso! A página será recarregada.");
            window.location.reload();
        } catch (error) {
            console.error(error);
            alert("Erro ao atualizar foto.");
        } finally {
            setLoading(false);
        }
    };

    const handleVerifyPassword = async (e) => {
        e?.preventDefault();
        setLoading(true);
        try {
            await api.post('/auth/verify-password/', { senha_atual: passwordData.currentPassword });
            setPasswordVerified(true);
        } catch (error) {
            console.error(error);
            setPasswordVerified(false);
            const errorMsg = error.response?.data?.error || "Senha incorreta.";
            alert(errorMsg);
        } finally {
            setLoading(false);
        }
    };

    const handleUpdatePassword = async (e) => {
        e.preventDefault();
        if (passwordData.newPassword !== passwordData.confirmPassword) {
            alert("As senhas não coincidem!");
            return;
        }

        setLoading(true);
        try {
            await api.post('/auth/change-password/', {
                senha_atual: passwordData.currentPassword,
                nova_senha: passwordData.newPassword
            });
            alert("Senha atualizada com sucesso!");
            setPasswordData({ currentPassword: '', newPassword: '', confirmPassword: '' });
            setPasswordVerified(false);
        } catch (error) {
            console.error(error);
            // Melhor feedback de erro
            const errorMsg = error.response?.data?.error || "Erro ao atualizar senha. Verifique sua senha atual.";
            alert(errorMsg);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className='containelGeralclient'>
            <Sidebar {...sidebarProp} />
            <main className='containelMainclient'>
                <Header text1="Minha Conta" text2="Perfil do Usuário" />

                <div className={style.profileGrid}>
                    {/* Informações Pessoais (Read-only) */}
                    <div className={style.card}>
                        <div className={style.profileInfoSide}>
                            {/* ... (Avatar and Info Code remains the same) ... */}
                            <div className={style.avatarContainer}>
                                <div className={style.avatar}>
                                    {previewImage ? (
                                        <img src={previewImage} alt="Preview" />
                                    ) : user?.img_path ? (
                                        <img src={user.img_path} alt="Profile" />
                                    ) : (
                                        <RiUserLine size={64} style={{ opacity: 0.5 }} />
                                    )}
                                    <label htmlFor="photo-upload" className={style.editOverlay}>
                                        <RiImageEditLine />
                                        <input type="file" id="photo-upload" hidden onChange={handleImageChange} accept="image/*" />
                                    </label>
                                </div>
                                {rawImage && (
                                    <button onClick={handleUpdatePhoto} className={style.saveBtn} disabled={loading}>
                                        {loading ? '...' : 'Salvar Foto'}
                                    </button>
                                )}
                            </div>

                            <div className={style.mainInfo}>
                                <h1>{user?.nome}</h1>
                                <span>{user?.tipo?.toUpperCase()}</span>
                            </div>
                        </div>

                        <div className={style.detailsGrid}>
                            <div className={style.detailItem}>
                                <RiMailLine />
                                <div>
                                    <label>Email</label>
                                    <p>{user?.email}</p>
                                </div>
                            </div>
                            {user?.tipo === 'aluno' && (
                                <div className={style.detailItem}>
                                    <RiUserLine />
                                    <div>
                                        <label>Nº Matrícula</label>
                                        <p>{user?.numero_matricula}</p>
                                    </div>
                                </div>
                            )}
                            {user?.tipo === 'funcionario' && (
                                <div className={style.detailItem}>
                                    <RiUserLine />
                                    <div>
                                        <label>Cargo</label>
                                        <p>{user?.cargo}</p>
                                    </div>
                                </div>
                            )}
                            <div className={style.detailItem}>
                                <RiMapPinLine />
                                <div>
                                    <label>Status</label>
                                    <p>{user?.status || 'Ativo'}</p>
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Segurança (Editable 2-Step) */}
                    <div className={style.card}>
                        <div className={style.cardHeader}>
                            <RiLockLine />
                            <h2>Alterar Senha</h2>
                        </div>

                        {!passwordVerified ? (
                            <form onSubmit={(e) => { e.preventDefault(); handleVerifyPassword(); }} className={style.passwordForm}>
                                <div className={style.inputGroup}>
                                    <label>Para continuar, digite sua senha atual</label>
                                    <input
                                        type="password"
                                        required
                                        placeholder="Senha Atual"
                                        value={passwordData.currentPassword}
                                        onChange={(e) => setPasswordData({ ...passwordData, currentPassword: e.target.value })}
                                    />
                                </div>
                                <button type="submit" className={style.submitBtn} disabled={loading || !passwordData.currentPassword}>
                                    {loading ? 'Verificando...' : 'Verificar Senha'}
                                </button>
                            </form>
                        ) : (
                            <form onSubmit={handleUpdatePassword} className={style.passwordForm}>
                                <div className={style.inputGroup}>
                                    <label style={{ color: 'var(--emerald-500)' }}>✓ Senha Atual Verificada</label>
                                    <input
                                        type="password"
                                        disabled
                                        value={passwordData.currentPassword}
                                        style={{ opacity: 0.7, borderColor: 'var(--emerald-500)' }}
                                    />
                                </div>
                                <div className={style.inputGroup}>
                                    <label>Nova Senha</label>
                                    <input
                                        type="password"
                                        required
                                        placeholder="Nova Senha"
                                        value={passwordData.newPassword}
                                        onChange={(e) => setPasswordData({ ...passwordData, newPassword: e.target.value })}
                                        autoFocus
                                    />
                                </div>
                                <div className={style.inputGroup}>
                                    <label>Confirmar Nova Senha</label>
                                    <input
                                        type="password"
                                        required
                                        placeholder="Repita a Nova Senha"
                                        value={passwordData.confirmPassword}
                                        onChange={(e) => setPasswordData({ ...passwordData, confirmPassword: e.target.value })}
                                    />
                                </div>
                                <div style={{ display: 'flex', gap: '10px' }}>
                                    <button
                                        type="button"
                                        className={style.submitBtn}
                                        style={{ background: 'var(--bg-hover)', color: 'var(--text-main)', flex: 1 }}
                                        onClick={() => {
                                            setPasswordVerified(false);
                                            setPasswordData({ ...passwordData, newPassword: '', confirmPassword: '' });
                                        }}
                                    >
                                        Cancelar
                                    </button>
                                    <button type="submit" className={style.submitBtn} disabled={loading} style={{ flex: 2 }}>
                                        {loading ? 'Atualizando...' : 'Confirmar Alteração'}
                                        <RiSaveLine />
                                    </button>
                                </div>
                            </form>
                        )}
                    </div>
                </div>
            </main>
        </div>
    );
};

export default Profile;
