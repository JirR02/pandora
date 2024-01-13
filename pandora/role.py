from __future__ import annotations

import json

from enum import Enum, unique, auto
from typing import Union, List, Dict, cast

from .exceptions import Unsupported
from .storage_client import Storage


@unique
class RoleName(Enum):
    admin = auto()
    owner = auto()
    reader = auto()
    other = auto()


@unique
class Action(Enum):
    submit_file = auto()
    read_analysis = auto()
    download_images = auto()
    download_pdf = auto()
    download_text = auto()
    see_text_preview = auto()
    download_zip = auto()
    download_misp = auto()
    refresh_analysis = auto()
    rescan_file = auto()
    notify_cert = auto()
    share_analysis = auto()
    delete_file = auto()
    list_own_tasks = auto()
    list_all_tasks = auto()
    search_file_name = auto()
    search_file_hash = auto()
    list_observables = auto()
    update_observable = auto()
    insert_observable = auto()
    list_users = auto()
    list_roles = auto()
    update_role = auto()
    list_stats = auto()
    manage_observables_lists = auto()
    submit_to_misp = auto()


class Role:

    def __init__(self, name: str, description: str, actions: dict[str, bool] | str):
        if name not in RoleName.__members__:
            raise Unsupported(f"unexpected role name '{name}'")
        self.storage = Storage()
        self.name = RoleName[name]
        self.description = description
        if isinstance(actions, str):
            actions = cast(Dict[str, bool], json.loads(actions))
        self.actions: dict[Action, bool] = {}
        for action_name, perm in actions.items():
            if action_name not in Action.__members__:
                raise Unsupported(f"unexpected action name '{action_name}'")
            self.actions[Action[action_name]] = perm

    @property
    def to_dict(self) -> dict[str, str]:
        to_return = {'name': str(self.name.name), 'description': self.description}
        to_return['actions'] = json.dumps({action.name: perm for action, perm in self.actions.items()})
        return to_return

    def store(self) -> None:
        self.storage.set_role(self.to_dict)

    def set_action(self, action: str | Action, value: bool) -> None:
        """
        Add boolean action for role.
        :param (str) action: model name
        :param (bool) value: model value
        """
        if isinstance(action, str):
            if action not in Action.__members__:
                raise Unsupported(f"unexpected action name '{action}'")
            action = Action[action]
        self.actions[action] = value

    def can(self, actions: str | list[str] | Action | list[Action], operator: str='and') -> bool:
        """
        Property that returns True if role can do an action
        :param actions: action or list of actions
        :param operator: and/or operator
        :return: whether if the role is allowed to do the action
        """
        if operator not in ('and', 'or'):
            raise Unsupported(f"unexpected operator '{operator}'")
        if isinstance(actions, str):
            actions = Action[actions]
        if isinstance(actions, list):
            if operator == 'and':
                return all(self.can(action) for action in actions)
            return any(self.can(action) for action in actions)
        if actions in self.actions:
            return self.actions[actions]
        return False

    @property
    def is_admin(self) -> bool:
        """
        Property to know if if is admin role
        :return (bool):
        """
        return self.name == RoleName.admin

    def __repr__(self) -> str:
        return str(self.to_dict)
