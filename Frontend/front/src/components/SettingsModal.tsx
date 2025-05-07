import React from 'react';

interface SettingsModalProps {
    isOpen: boolean;
    onClose: () => void;
    onDeleteAccount: () => void;
    onModifyUserData: () => void;
}

const SettingsModal: React.FC<SettingsModalProps> = ({ isOpen, onClose, onDeleteAccount, onModifyUserData }) => {
    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 bg-black/10 backdrop-blur-sm flex items-center justify-center z-50 overflow-hidden">
            <div className="bg-white rounded-xl p-6 w-full max-w-2xl max-h-120 overflow-y-auto shadow-lg">
                <h2 className="text-xl font-bold mb-4 text-gray-700">Ajustes de la cuenta</h2>
                <div className="space-y-4">
                    <button
                        onClick={onModifyUserData}
                        className="w-full text-left px-4 py-2 bg-blue-100 hover:bg-blue-200 text-gray-700 rounded-md transition-all cursor-pointer"
                    >
                        Modificar datos de usuario
                    </button>
                    <button
                        onClick={onDeleteAccount}
                        className="w-full text-left px-4 py-2 bg-red-100 hover:bg-red-200 text-gray-700 rounded-md transition-all cursor-pointer"
                    >
                        Eliminar cuenta
                    </button>


                </div>
                <button
                    onClick={onClose}
                    className="mt-6 w-full bg-gray-200 hover:bg-gray-300 text-gray-700 rounded-md px-4 py-2 transition-all cursor-pointer"
                >
                    Cerrar
                </button>
            </div>
        </div>
    );
};

export default SettingsModal;
