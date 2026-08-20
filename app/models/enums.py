"""
System-wide Enums and Role-Based Access Control (RBAC).
Archdiocese of Kigali Ecclesiastical Authority Model.
"""
from enum import Enum
from typing import List, Set


class UserRole(str, Enum):
    """System and ecclesiastical roles mirroring diocesan governance."""

    SUPER_ADMIN = "SUPER_ADMIN"              # Archdiocesan IT / System Administrator
    ARCHBISHOP = "ARCHBISHOP"                # Archevêque de Kigali
    VICAR_GENERAL = "VICAR_GENERAL"          # Vicaire Général
    CHANCELLOR = "CHANCELLOR"                # Chancelier (Official decrees & registers)
    ECONOMO = "ECONOMO"                      # Économe diocésain (Treasurer / Land & Assets)
    DEAN = "DEAN"                            # Curé de Doyenné / Vicaire Forane
    PARISH_PRIEST = "PARISH_PRIEST"          # Curé de Paroisse
    PARISH_VICAR = "PARISH_VICAR"            # Vicaire paroissial
    PARISH_SECRETARY = "PARISH_SECRETARY"    # Secrétaire paroissial
    MINISTRY_LEADER = "MINISTRY_LEADER"      # Responsable de commission / mouvement
    READ_ONLY_AUDITOR = "READ_ONLY_AUDITOR"  # Auditeur / Statisticien


# Hierarchy mapping (higher roles inherit lower permissions)
ROLE_HIERARCHY: dict[UserRole, Set[UserRole]] = {
    UserRole.SUPER_ADMIN: set(UserRole),
    UserRole.ARCHBISHOP: {
        UserRole.ARCHBISHOP,
        UserRole.VICAR_GENERAL,
        UserRole.CHANCELLOR,
        UserRole.ECONOMO,
        UserRole.DEAN,
        UserRole.PARISH_PRIEST,
        UserRole.PARISH_VICAR,
        UserRole.PARISH_SECRETARY,
        UserRole.READ_ONLY_AUDITOR,
    },
    UserRole.VICAR_GENERAL: {
        UserRole.VICAR_GENERAL,
        UserRole.CHANCELLOR,
        UserRole.ECONOMO,
        UserRole.DEAN,
        UserRole.PARISH_PRIEST,
        UserRole.PARISH_VICAR,
        UserRole.PARISH_SECRETARY,
        UserRole.READ_ONLY_AUDITOR,
    },
    UserRole.CHANCELLOR: {
        UserRole.CHANCELLOR,
        UserRole.DEAN,
        UserRole.PARISH_PRIEST,
        UserRole.PARISH_VICAR,
        UserRole.PARISH_SECRETARY,
        UserRole.READ_ONLY_AUDITOR,
    },
    UserRole.ECONOMO: {
        UserRole.ECONOMO,
        UserRole.DEAN,
        UserRole.PARISH_PRIEST,
        UserRole.PARISH_SECRETARY,
        UserRole.READ_ONLY_AUDITOR,
    },
    UserRole.DEAN: {
        UserRole.DEAN,
        UserRole.PARISH_PRIEST,
        UserRole.PARISH_VICAR,
        UserRole.PARISH_SECRETARY,
        UserRole.READ_ONLY_AUDITOR,
    },
    UserRole.PARISH_PRIEST: {
        UserRole.PARISH_PRIEST,
        UserRole.PARISH_VICAR,
        UserRole.PARISH_SECRETARY,
        UserRole.MINISTRY_LEADER,
        UserRole.READ_ONLY_AUDITOR,
    },
    UserRole.PARISH_VICAR: {
        UserRole.PARISH_VICAR,
        UserRole.PARISH_SECRETARY,
        UserRole.MINISTRY_LEADER,
        UserRole.READ_ONLY_AUDITOR,
    },
    UserRole.PARISH_SECRETARY: {
        UserRole.PARISH_SECRETARY,
        UserRole.READ_ONLY_AUDITOR,
    },
    UserRole.MINISTRY_LEADER: {
        UserRole.MINISTRY_LEADER,
    },
    UserRole.READ_ONLY_AUDITOR: {
        UserRole.READ_ONLY_AUDITOR,
    },
}


def has_role(user_role: UserRole, required_roles: List[UserRole]) -> bool:
    """Check whether the user's role satisfies any required role according to the hierarchy."""
    accessible_roles = ROLE_HIERARCHY.get(user_role, {user_role})
    return any(req in accessible_roles for req in required_roles)
