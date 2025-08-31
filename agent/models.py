# Data models for learner profile service

# Event type constants
EVENT_USER_CREATED = "user_created"
EVENT_ASSESSMENT_SUBMITTED = "assessment_submitted"
EVENT_MODULE_COMPLETED = "module_completed"

from dataclasses import dataclass, asdict, field
from typing import Dict, List, Optional, Any, Type, TypeVar

T = TypeVar('T')

def from_dict(cls: Type[T], data: dict) -> T:
	"""Generic from_dict for dataclasses."""
	return cls(**data)

def to_dict(obj: Any) -> dict:
	"""Generic to_dict for dataclasses."""
	if hasattr(obj, 'to_dict'):
		return obj.to_dict()
	return asdict(obj)

@dataclass
class Skill:
	level: float
	confidence: float

@dataclass
class UserSkillProfile:
	user_id: str
	role_id: str
	skills: Dict[str, Skill]

	@staticmethod
	def from_dict(data: dict) -> 'UserSkillProfile':
		skills = {k: Skill(**v) for k, v in data.get('skills', {}).items()}
		return UserSkillProfile(
			user_id=data['user_id'],
			role_id=data['role_id'],
			skills=skills
		)

	def to_dict(self) -> dict:
		return {
			'user_id': self.user_id,
			'role_id': self.role_id,
			'skills': {k: asdict(v) for k, v in self.skills.items()}
		}

@dataclass
class FocusPoint:
	skill: str
	gap: float
	importance: int = 1

@dataclass
class FocusAreas:
	points: List[FocusPoint]

	def top_n(self, n: int = 3) -> List[FocusPoint]:
		return sorted(self.points, key=lambda x: (-x.gap, -x.importance))[:n]

	@staticmethod
	def from_list(lst: List[dict]) -> 'FocusAreas':
		return FocusAreas([FocusPoint(**d) for d in lst])

	def to_list(self) -> List[dict]:
		return [asdict(p) for p in self.points]

@dataclass
class ModuleMeta:
	skill: str
	target_level: float
	weight: float = 1.0
	has_assessment: bool = False
	pass_threshold: Optional[float] = None

	@staticmethod
	def from_dict(data: dict) -> 'ModuleMeta':
		return ModuleMeta(**data)

	def to_dict(self) -> dict:
		return asdict(self)

@dataclass
class JDRequirements:
	role_id: str
	skills: Dict[str, Dict[str, Any]]  # {skill: {required_level, importance}}

	@staticmethod
	def from_dict(data: dict) -> 'JDRequirements':
		return JDRequirements(
			role_id=data['role_id'],
			skills=data['skills']
		)

	def to_dict(self) -> dict:
		return asdict(self)

@dataclass
class Event:
	user_id: str
	skill: str
	target_level: float
	completion_type: str
	has_assessment: bool = False
	score: Optional[float] = None
	pass_threshold: Optional[float] = None
	weight: float = 1.0

	@staticmethod
	def from_dict(data: dict) -> 'Event':
		return Event(**data)

	def to_dict(self) -> dict:
		return asdict(self)
