#!/usr/bin/env python3
"""
Device detection and capability assessment for AI model hosting.
Automatically detects hardware and recommends best AI setup.
"""

import os
import re
import subprocess
import platform
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class DeviceDetector:
    """Detect device capabilities and provide AI hosting recommendations."""

    def __init__(self):
        self.info = self._detect_device()
        self.capabilities = self._assess_capabilities()
        self.recommendations = self._generate_recommendations()

    def _detect_device(self) -> Dict:
        """Detect device information."""
        info = {
            'platform': platform.system(),
            'machine': platform.machine(),
            'processor': platform.processor(),
            'is_android': False,
            'manufacturer': 'Unknown',
            'model': 'Unknown',
            'soc': 'Unknown',
            'ram_mb': 0,
            'has_npu': False,
            'cpu_cores': os.cpu_count() or 1,
        }

        # Detect Android
        if os.path.exists('/system/build.prop'):
            info['is_android'] = True
            info.update(self._detect_android_device())

        # Detect RAM
        info['ram_mb'] = self._detect_ram()

        return info

    def _detect_android_device(self) -> Dict:
        """Detect Android-specific information."""
        android_info = {
            'manufacturer': 'Unknown',
            'model': 'Unknown',
            'soc': 'Unknown',
            'has_npu': False,
            'android_version': 'Unknown',
        }

        try:
            # Read build.prop
            with open('/system/build.prop', 'r') as f:
                build_prop = f.read()

            # Extract manufacturer
            match = re.search(r'ro\.product\.manufacturer=(.+)', build_prop)
            if match:
                android_info['manufacturer'] = match.group(1).strip()

            # Extract model
            match = re.search(r'ro\.product\.model=(.+)', build_prop)
            if match:
                android_info['model'] = match.group(1).strip()

            # Extract Android version
            match = re.search(r'ro\.build\.version\.release=(.+)', build_prop)
            if match:
                android_info['android_version'] = match.group(1).strip()

        except Exception as e:
            print(f"Warning: Could not read build.prop: {e}")

        # Detect SoC via getprop
        try:
            result = subprocess.run(
                ['getprop', 'ro.hardware'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                hardware = result.stdout.strip().lower()

                # Detect specific SoCs
                if 'tensor' in hardware:
                    android_info['soc'] = 'Google Tensor'
                    android_info['has_npu'] = True

                    # Try to get Tensor version
                    if os.path.exists('/sys/devices/platform/soc/'):
                        # G5 detection (Pixel 10)
                        if any('zuma' in str(p) for p in Path('/sys/devices/platform/soc/').glob('*')):
                            android_info['soc'] = 'Tensor G5'
                        # G4 detection (Pixel 9)
                        elif any('ripcurrent' in str(p) for p in Path('/sys/devices/platform/soc/').glob('*')):
                            android_info['soc'] = 'Tensor G4'
                        # G3 detection (Pixel 8)
                        elif any('zuma' in str(p) for p in Path('/sys/devices/platform/soc/').glob('*')):
                            android_info['soc'] = 'Tensor G3'

                elif 'snapdragon' in hardware or 'qcom' in hardware:
                    android_info['soc'] = 'Qualcomm Snapdragon'
                    # Snapdragon 8 Gen 2+ have NPU
                    if '8gen' in hardware:
                        android_info['has_npu'] = True

                elif 'exynos' in hardware:
                    android_info['soc'] = 'Samsung Exynos'

                elif 'mediatek' in hardware or 'mtk' in hardware:
                    android_info['soc'] = 'MediaTek'

                else:
                    android_info['soc'] = hardware.title()

        except Exception as e:
            print(f"Warning: Could not detect SoC: {e}")

        # Detect NPU via other methods
        if not android_info['has_npu']:
            # Check for NPU kernel modules
            if os.path.exists('/sys/class/npu'):
                android_info['has_npu'] = True
            elif os.path.exists('/dev/npu'):
                android_info['has_npu'] = True

        return android_info

    def _detect_ram(self) -> int:
        """Detect available RAM in MB."""
        try:
            # Try meminfo (Linux/Android)
            if os.path.exists('/proc/meminfo'):
                with open('/proc/meminfo', 'r') as f:
                    for line in f:
                        if line.startswith('MemTotal:'):
                            kb = int(line.split()[1])
                            return kb // 1024

            # Fallback methods for other platforms
            if platform.system() == 'Darwin':  # macOS
                result = subprocess.run(
                    ['sysctl', '-n', 'hw.memsize'],
                    capture_output=True,
                    text=True
                )
                if result.returncode == 0:
                    bytes_ram = int(result.stdout.strip())
                    return bytes_ram // (1024 * 1024)

        except Exception as e:
            print(f"Warning: Could not detect RAM: {e}")

        return 0

    def _assess_capabilities(self) -> Dict:
        """Assess device capabilities for AI model hosting."""
        caps = {
            'can_run_local': False,
            'recommended_model_size': '1B',
            'max_model_size': '1B',
            'npu_available': self.info['has_npu'],
            'cpu_score': 0,
            'ram_score': 0,
            'overall_score': 0,
            'performance_tier': 'Low',
        }

        # RAM assessment
        ram_mb = self.info['ram_mb']
        if ram_mb >= 12288:  # 12GB+
            caps['ram_score'] = 100
            caps['max_model_size'] = '7B'
            caps['recommended_model_size'] = '3B'
        elif ram_mb >= 8192:  # 8GB
            caps['ram_score'] = 80
            caps['max_model_size'] = '3B'
            caps['recommended_model_size'] = '3B'
        elif ram_mb >= 6144:  # 6GB
            caps['ram_score'] = 60
            caps['max_model_size'] = '3B'
            caps['recommended_model_size'] = '1B'
        elif ram_mb >= 4096:  # 4GB
            caps['ram_score'] = 40
            caps['max_model_size'] = '1B'
            caps['recommended_model_size'] = '1B'
        elif ram_mb >= 2048:  # 2GB
            caps['ram_score'] = 20
            caps['max_model_size'] = '1B'
            caps['recommended_model_size'] = 'TinyLlama'
        else:
            caps['ram_score'] = 10
            caps['max_model_size'] = 'TinyLlama'
            caps['recommended_model_size'] = 'API-only'

        # CPU assessment
        cores = self.info['cpu_cores']
        if cores >= 8:
            caps['cpu_score'] = 100
        elif cores >= 6:
            caps['cpu_score'] = 80
        elif cores >= 4:
            caps['cpu_score'] = 60
        elif cores >= 2:
            caps['cpu_score'] = 40
        else:
            caps['cpu_score'] = 20

        # NPU bonus
        if caps['npu_available']:
            caps['cpu_score'] = min(100, caps['cpu_score'] + 20)

        # Overall assessment
        caps['overall_score'] = (caps['ram_score'] + caps['cpu_score']) // 2

        if caps['overall_score'] >= 80:
            caps['performance_tier'] = 'High'
            caps['can_run_local'] = True
        elif caps['overall_score'] >= 60:
            caps['performance_tier'] = 'Medium'
            caps['can_run_local'] = True
        elif caps['overall_score'] >= 40:
            caps['performance_tier'] = 'Low'
            caps['can_run_local'] = True
        else:
            caps['performance_tier'] = 'Very Low'
            caps['can_run_local'] = False

        return caps

    def _generate_recommendations(self) -> Dict:
        """Generate AI hosting recommendations."""
        recs = {
            'primary_mode': 'API',
            'can_use_local': False,
            'can_use_ssh': True,
            'can_use_api': True,
            'local_models': [],
            'reasons': [],
            'warnings': [],
            'tips': [],
        }

        # Determine primary mode
        if self.capabilities['overall_score'] >= 70:
            recs['primary_mode'] = 'Local'
            recs['can_use_local'] = True
            recs['reasons'].append(f"Good device performance (score: {self.capabilities['overall_score']}/100)")

        elif self.capabilities['overall_score'] >= 40:
            recs['primary_mode'] = 'Hybrid'
            recs['can_use_local'] = True
            recs['reasons'].append("Medium performance - use local for simple tasks, API for complex")

        else:
            recs['primary_mode'] = 'API'
            recs['reasons'].append("Low performance - API recommended for best experience")
            recs['warnings'].append("Local models may be slow on this device")

        # Recommend models
        if recs['can_use_local']:
            max_size = self.capabilities['recommended_model_size']

            if max_size in ['7B', '3B']:
                recs['local_models'] = [
                    {'name': 'llama3.2:3b', 'size': '3B', 'quality': 'High', 'speed': 'Medium'},
                    {'name': 'phi3:mini', 'size': '3.8B', 'quality': 'High', 'speed': 'Medium'},
                ]

            if max_size in ['7B', '3B', '1B']:
                recs['local_models'].append(
                    {'name': 'llama3.2:1b', 'size': '1B', 'quality': 'Good', 'speed': 'Fast'}
                )

            if max_size == 'TinyLlama':
                recs['local_models'] = [
                    {'name': 'tinyllama', 'size': '1.1B', 'quality': 'Basic', 'speed': 'Very Fast'}
                ]

        # NPU-specific recommendations
        if self.capabilities['npu_available']:
            recs['tips'].append("NPU detected! Use Gemini Nano if available for best performance")

            # Tensor-specific
            if 'Tensor' in self.info['soc']:
                recs['tips'].append(f"{self.info['soc']} detected - optimized for on-device AI")

                if 'G5' in self.info['soc']:
                    recs['tips'].append("Tensor G5 can handle larger models efficiently")
                    if self.capabilities['max_model_size'] == '1B':
                        recs['tips'].append("Consider upgrading to 3B model - your chip can handle it")

        # RAM warnings
        if self.info['ram_mb'] < 4096:
            recs['warnings'].append(f"Low RAM ({self.info['ram_mb']}MB) - local models may cause slowdowns")

        # Battery tips
        if self.info['is_android']:
            recs['tips'].append("Local models use more battery - use SSH/API when not charging")

        # SSH always viable
        recs['reasons'].append("SSH to home network is always available for powerful models")

        return recs

    def get_summary(self) -> str:
        """Get human-readable summary."""
        lines = []

        lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        lines.append("DEVICE ANALYSIS")
        lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

        # Device info
        if self.info['is_android']:
            lines.append(f"\n📱 Device: {self.info['manufacturer']} {self.info['model']}")
            lines.append(f"   SoC: {self.info['soc']}")
        else:
            lines.append(f"\n💻 Platform: {self.info['platform']}")
            lines.append(f"   Processor: {self.info['processor']}")

        lines.append(f"   RAM: {self.info['ram_mb']}MB")
        lines.append(f"   CPU Cores: {self.info['cpu_cores']}")
        lines.append(f"   NPU: {'✓ Available' if self.capabilities['npu_available'] else '✗ Not detected'}")

        # Performance
        lines.append(f"\n⚡ Performance Tier: {self.capabilities['performance_tier']}")
        lines.append(f"   Overall Score: {self.capabilities['overall_score']}/100")
        lines.append(f"   Max Model Size: {self.capabilities['max_model_size']}")

        # Recommendations
        lines.append(f"\n🎯 Recommended Setup: {self.recommendations['primary_mode']}")

        if self.recommendations['can_use_local']:
            lines.append("\n✅ Local Models:")
            for model in self.recommendations['local_models']:
                lines.append(f"   • {model['name']} - {model['quality']} quality, {model['speed']} speed")
        else:
            lines.append("\n⚠️  Local models not recommended for this device")

        # Reasons
        if self.recommendations['reasons']:
            lines.append("\n📋 Why:")
            for reason in self.recommendations['reasons']:
                lines.append(f"   • {reason}")

        # Warnings
        if self.recommendations['warnings']:
            lines.append("\n⚠️  Warnings:")
            for warning in self.recommendations['warnings']:
                lines.append(f"   • {warning}")

        # Tips
        if self.recommendations['tips']:
            lines.append("\n💡 Tips:")
            for tip in self.recommendations['tips']:
                lines.append(f"   • {tip}")

        lines.append("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

        return '\n'.join(lines)

    def get_ui_recommendations(self) -> Dict:
        """Get recommendations formatted for UI display."""
        return {
            'device_name': f"{self.info.get('manufacturer', 'Unknown')} {self.info.get('model', 'Device')}",
            'soc': self.info.get('soc', 'Unknown'),
            'ram_mb': self.info['ram_mb'],
            'has_npu': self.capabilities['npu_available'],
            'performance_tier': self.capabilities['performance_tier'],
            'score': self.capabilities['overall_score'],
            'primary_mode': self.recommendations['primary_mode'],
            'can_use_local': self.recommendations['can_use_local'],
            'recommended_models': self.recommendations['local_models'],
            'warnings': self.recommendations['warnings'],
            'tips': self.recommendations['tips'],
        }


def detect_and_recommend():
    """Convenience function to detect device and get recommendations."""
    detector = DeviceDetector()
    return detector


if __name__ == '__main__':
    # Run detection
    detector = DeviceDetector()
    print(detector.get_summary())
