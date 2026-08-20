import React from 'react';
import { Modal } from '../../components/common/Modal';
import { Input } from '../../components/common/Input';
import { Button } from '../../components/common/Button';

interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const FaithfulCreateModal: React.FC<ModalProps> = ({ isOpen, onClose }) => {
  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Register New Parishioner (Kwandika Umukristu)" maxWidth="lg">
      <form className="space-y-4" onSubmit={(e) => { e.preventDefault(); onClose(); }}>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <Input label="Last Name (Izina ry'umuryango)" placeholder="Mugisha" required />
          <Input label="First Name (Izina ry'irigeno)" placeholder="Jean-Baptiste" required />
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <Input label="Christian Name (Izina rya Batisimu)" placeholder="Jean-Baptiste" required />
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Gender</label>
            <select className="w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm text-sm focus:outline-none focus:ring-brand-500">
              <option value="MALE">Male (Gabo)</option>
              <option value="FEMALE">Female (Gore)</option>
            </select>
          </div>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <Input label="National ID (Indangamuntu)" placeholder="11990800..." />
          <Input label="Phone Number" placeholder="+250 788 000 000" />
        </div>
        <div className="flex justify-end gap-2 pt-4 border-t border-gray-100">
          <Button variant="outline" type="button" onClick={onClose}>Cancel</Button>
          <Button type="submit">Save Faithful</Button>
        </div>
      </form>
    </Modal>
  );
};
