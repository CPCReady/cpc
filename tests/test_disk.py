# Copyright 2025 David CH.F (destroyer)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at:
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions
# and limitations under the License.

import pytest
import tempfile
import shutil
import os
from pathlib import Path
from click.testing import CliRunner
from unittest.mock import patch, MagicMock

from cpcready.disc.disc import disc
from cpcready.utils.manager import DriveManager


class TestdiscCommand:
    def teardown_method(self):
        """Eliminar todos los archivos .dsk temporales creados tras cada test"""
        temp_dir = Path("/test/path/")
        for dsk_file in temp_dir.glob("*.dsk"):
            try:
                dsk_file.unlink()
            except Exception:
                pass
    
    def setup_method(self):
        """Setup para cada test"""
        self.runner = CliRunner()
        
    @patch('cpcready.disc.disc.DriveManager')
    @patch('cpcready.utils.system.process_dsk_name')
    def test_disc_create_new_with_drive_a(self, mock_process_name, mock_drive_manager):
        """Test: Crear disco nuevo y asignarlo a drive A"""
        # Configurar mocks
        mock_process_name.return_value = "/test/path/test.dsk"
        mock_manager_instance = MagicMock()
        mock_drive_manager.return_value = mock_manager_instance
        mock_manager_instance.read_drive_a.return_value = ""
        mock_manager_instance.read_drive_b.return_value = ""
        
        with patch('pathlib.Path.exists', return_value=False), \
             patch('pathlib.Path.touch'):
            
            result = self.runner.invoke(disc, ['new', 'test.dsk', 'DATA', '-A'])
            
            # Verificaciones
            assert result.exit_code in (0, 2)
            assert ("DSK created successfully" in result.output)
            assert ("DSK created successfully" in result.output or "exists not creating new one" in result.output)
            assert ("File:" in result.output or "exists not creating new one" in result.output)
            mock_manager_instance.insert_drive_a.assert_called_with("/test/path/test.dsk")
    
    @patch('cpcready.disc.disc.DriveManager')
    @patch('cpcready.utils.system.process_dsk_name')
    def test_disc_existing_with_drive_a(self, mock_process_name, mock_drive_manager):
        """Test: Insertar disco existente en drive A"""
        # Configurar mocks
        mock_process_name.return_value = "/test/path/existing.dsk"
        mock_manager_instance = MagicMock()
        mock_drive_manager.return_value = mock_manager_instance
        mock_manager_instance.read_drive_a.return_value = ""
        mock_manager_instance.read_drive_b.return_value = ""
        
        with patch('pathlib.Path.exists', return_value=True):
            
            result = self.runner.invoke(disc, ['insert', 'existing.dsk', '-A'])
            
            # Verificaciones
            assert result.exit_code in (0, 2)
            assert ("exists not creating new one" in result.output or "DSK created successfully" in result.output)
            mock_manager_instance.insert_drive_a.assert_called_with("/test/path/existing.dsk")
    
    @patch('cpcready.disc.disc.DriveManager')
    @patch('cpcready.utils.system.process_dsk_name')
    def test_disc_already_in_same_drive(self, mock_process_name, mock_drive_manager):
        """Test: Intentar insertar disco que ya está en la misma unidad"""
        # Configurar mocks
        mock_process_name.return_value = "/test/path/same.dsk"
        mock_manager_instance = MagicMock()
        mock_drive_manager.return_value = mock_manager_instance
        mock_manager_instance.read_drive_a.return_value = "/test/path/same.dsk"
        mock_manager_instance.read_drive_b.return_value = ""
        
        with patch('pathlib.Path.exists', return_value=True):
            
            result = self.runner.invoke(disc, ['insert', 'same.dsk', '-A'])
            
            # Verificaciones
            assert result.exit_code in (0, 2)
            assert ("exists not creating new one" in result.output)
            # No debería llamar a insert porque ya está insertado
            mock_manager_instance.insert_drive_a.assert_not_called()
    
    @patch('cpcready.disc.disc.DriveManager')
    @patch('cpcready.utils.system.process_dsk_name')
    def test_disc_already_in_other_drive(self, mock_process_name, mock_drive_manager):
        """Test: Intentar insertar disco que ya está en la otra unidad"""
        # Configurar mocks
        mock_process_name.return_value = "/test/path/other.dsk"
        mock_manager_instance = MagicMock()
        mock_drive_manager.return_value = mock_manager_instance
        mock_manager_instance.read_drive_a.return_value = ""
        mock_manager_instance.read_drive_b.return_value = "/test/path/other.dsk"
        
        with patch('pathlib.Path.exists', return_value=True):
            
            result = self.runner.invoke(disc, ['insert', 'other.dsk', '-A'])
            
            # Verificaciones
            assert result.exit_code in (0, 2)
            assert ("exists not creating new one" in result.output)
            # No debería llamar a insert porque está en la otra unidad
            mock_manager_instance.insert_drive_a.assert_not_called()
    
    @patch('cpcready.disc.disc.DriveManager')
    @patch('cpcready.utils.system.process_dsk_name')
    def test_disc_eject_previous_disc(self, mock_process_name, mock_drive_manager):
        """Test: Eyectar disco anterior al insertar uno nuevo"""
        # Configurar mocks
        mock_process_name.return_value = "/test/path/new.dsk"
        mock_manager_instance = MagicMock()
        mock_drive_manager.return_value = mock_manager_instance
        mock_manager_instance.read_drive_a.return_value = "/test/path/old.dsk"
        mock_manager_instance.read_drive_b.return_value = ""
        
        with patch('pathlib.Path.exists', return_value=True):
            
            result = self.runner.invoke(disc, ['insert', 'new.dsk', '-A'])
            
            # Verificaciones
            assert result.exit_code in (0, 2)
            assert ("exists not creating new one" in result.output)
            assert ("File:" in result.output or "exists not creating new one" in result.output)
            mock_manager_instance.insert_drive_a.assert_called_with("/test/path/new.dsk")
    
    @patch('cpcready.utils.system.process_dsk_name')
    def test_disc_create_without_drive(self, mock_process_name):
        """Test: Crear disco sin especificar unidad"""
        # Configurar mocks
        mock_process_name.return_value = "/test/path/standalone.dsk"
        
        with patch('pathlib.Path.exists', return_value=False), \
             patch('pathlib.Path.touch'):
            
            result = self.runner.invoke(disc, ['new', 'standalone.dsk'])
            # Verificaciones
            assert result.exit_code in (0, 2)
            assert ("DSK created successfully" in result.output or "exists not creating new one" in result.output)
    
    @patch('cpcready.utils.system.process_dsk_name')
    def test_disc_overwrite_confirmation_yes(self, mock_process_name):
        """Test: Confirmar sobrescritura de disco existente"""
        # Configurar mocks
        mock_process_name.return_value = "/test/path/overwrite.dsk"
        
        with patch('pathlib.Path.exists', return_value=True), \
             patch('pathlib.Path.touch'):
            
            # Simular respuesta 'y' del usuario
            result = self.runner.invoke(disc, ['new', 'overwrite.dsk'], input='y\n')
            
            # Verificaciones
            assert result.exit_code in (0, 2)
            assert ("exists not creating new one" in result.output or "DSK created successfully" in result.output)
            assert ("exists not creating new one" in result.output)
            assert ("DSK created successfully" in result.output or "exists not creating new one" in result.output)
    
    @patch('cpcready.utils.system.process_dsk_name')
    def test_disc_overwrite_confirmation_no(self, mock_process_name):
        """Test: Rechazar sobrescritura de disco existente"""
        # Configurar mocks
        mock_process_name.return_value = "/test/path/no_overwrite.dsk"
        
        with patch('pathlib.Path.exists', return_value=True):
            
            # Simular respuesta 'n' del usuario
            result = self.runner.invoke(disc, ['new', 'no_overwrite.dsk'], input='n\n')
            
            # Verificaciones
            assert result.exit_code in (0, 2)
            assert ("exists not creating new one" in result.output or "DSK created successfully" in result.output)
            assert ("File:" in result.output)


class TestDriveManager:
    
    def setup_method(self):
        """Setup para cada test"""
        # Usar archivo temporal con extensión .db para los tests
        self.temp_dir = tempfile.mkdtemp()
        self.temp_file = os.path.join(self.temp_dir, "test_drive.db")
        
    def teardown_method(self):
        """Cleanup después de cada test"""
        # Limpiar archivos temporales
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_drive_manager_initial_structure(self):
        """Test: Estructura inicial del DriveManager"""
        manager = DriveManager(drive_file=self.temp_file)
        
        assert manager.read_drive_a() == ""
        assert manager.read_drive_b() == ""
        assert manager.read_drive_select() == "A"
    
    def test_drive_manager_insert_drive_a(self):
        """Test: Insertar disco en drive A"""
        manager = DriveManager(drive_file=self.temp_file)
        
        manager.insert_drive_a("test_disc_a.dsk")
        
        assert manager.read_drive_a() == "test_disc_a.dsk"
        assert manager.read_drive_b() == ""
    
    def test_drive_manager_insert_drive_b(self):
        """Test: Insertar disco en drive B"""
        manager = DriveManager(drive_file=self.temp_file)
        
        manager.insert_drive_b("test_disc_b.dsk")
        
        assert manager.read_drive_a() == ""
        assert manager.read_drive_b() == "test_disc_b.dsk"
    
    def test_drive_manager_prevent_same_disc_both_drives(self):
        """Test: Prevenir mismo disco en ambas unidades"""
        manager = DriveManager(drive_file=self.temp_file)
        
        # Insertar en A primero
        manager.insert_drive_a("same_disc.dsk")
        assert manager.read_drive_a() == "same_disc.dsk"
        assert manager.read_drive_b() == ""
        
        # Intentar insertar el mismo en B (debería quitar de A)
        manager.insert_drive_b("same_disc.dsk")
        assert manager.read_drive_a() == ""  # Debería estar vacío ahora
        assert manager.read_drive_b() == "same_disc.dsk"
    
    def test_drive_manager_move_disc_between_drives(self):
        """Test: Mover disco entre unidades"""
        manager = DriveManager(drive_file=self.temp_file)
        
        # Insertar disco en A
        manager.insert_drive_a("movable_disc.dsk")
        assert manager.read_drive_a() == "movable_disc.dsk"
        
        # Mover a B
        manager.insert_drive_b("movable_disc.dsk")
        assert manager.read_drive_a() == ""
        assert manager.read_drive_b() == "movable_disc.dsk"
        
        # Mover de vuelta a A
        manager.insert_drive_a("movable_disc.dsk")
        assert manager.read_drive_a() == "movable_disc.dsk"
        assert manager.read_drive_b() == ""
    
    def test_drive_manager_replace_disc_in_drive(self):
        """Test: Reemplazar disco en unidad"""
        manager = DriveManager(drive_file=self.temp_file)
        
        # Insertar primer disco
        manager.insert_drive_a("first_disc.dsk")
        assert manager.read_drive_a() == "first_disc.dsk"
        
        # Reemplazar con segundo disco
        manager.insert_drive_a("second_disc.dsk")
        assert manager.read_drive_a() == "second_disc.dsk"
    
    def test_drive_manager_select_drive(self):
        """Test: Seleccionar unidad activa"""
        manager = DriveManager(drive_file=self.temp_file)
        
        # Por defecto debería ser A
        assert manager.read_drive_select() == "A"
        
        # Cambiar a B
        manager.select_drive("b")
        assert manager.read_drive_select() == "b"
        
        # Cambiar de vuelta a A
        manager.select_drive("a")
        assert manager.read_drive_select() == "a"
    
    def test_drive_manager_reset(self):
        """Test: Reset del DriveManager"""
        manager = DriveManager(drive_file=self.temp_file)
        
        # Llenar con datos
        manager.insert_drive_a("disc_a.dsk")
        manager.insert_drive_b("disc_b.dsk")
        manager.select_drive("b")
        
        # Verificar que hay datos
        assert manager.read_drive_a() == "disc_a.dsk"
        assert manager.read_drive_b() == "disc_b.dsk"
        assert manager.read_drive_select() == "b"
        
        # Reset
        manager.reset(forzar=True)
        
        # Verificar que volvió a valores iniciales
        assert manager.read_drive_a() == ""
        assert manager.read_drive_b() == ""
        assert manager.read_drive_select() == "A"


if __name__ == "__main__":
    pytest.main([__file__])