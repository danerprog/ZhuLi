from .MessageTask import MessageTask

import asyncio
import functools

class ListPermissionsTask(MessageTask):
    
    def __init__(self, **context):
        super().__init__(**context)
        self._initializeMemberVariables()
        self._logger.debug("initialized")
        
    async def run(self):
        self._logger.debug("run called.")
        await self._listPermissions()
        
    def _initializeMemberVariables(self):
        self._events = self._context['preprocessed_message'].tokens()[2:]
        self._guild = self._context['preprocessed_message'].raw().guild
        self._permissions_manager = self._context['permissions_manager']
        self._task = None
        
    async def _listPermissions(self):
        self._logger.debug("_listPermissions called.")
        events_to_list = self._events
        if events_to_list is None or len(events_to_list) <= 0:
            events_to_list = self._getListOfPossibleEvents()
        self._reply = await self._getPermissionMessagesFor(events_to_list)
        self._logger.debug("_listPermissions done.")
            
    async def _getPermissionMessagesFor(self, events_to_list):
        self._logger.debug(f"_getPermissionMessagesFor called. events_to_list: {events_to_list}")
        tasks = []
        for event in events_to_list:
            self._logger.debug(f"running _getPermissionMessagesFor('{event}') in parallel.")
            tasks.append(asyncio.create_task(self._getPermissionsMessageFor(event)))
        return await asyncio.gather(*tasks)
            
    async def _getPermissionsMessageFor(self, event):
        self._logger.debug(f"_getPermissionMessagesFor called. event: {event}")
        message = {
            "title" : f"list permissions {event}",
            "description" : f"User and Role permissions for command: {event}",
            "level" : "info",
            "fields" : []
        }
        user_permissions_string, role_permissions_string = await asyncio.gather(
            asyncio.create_task(self._getUserPermissionsInStringFor(event)),
            asyncio.create_task(self._getRolePermissionsInStringFor(event))
        )
        if len(user_permissions_string) > 0:
            message["fields"].append({
                "name" : "Users",
                "value" : user_permissions_string,
                "inline" : True
            })
        if len(role_permissions_string) > 0:
             message["fields"].append({
                "name" : "Roles",
                "value" : role_permissions_string,
                "inline" : True
            })
        self._logger.debug(f"_getPermissionsMessageFor called. message: {message}")
        return message
        
    def _getListOfPossibleEvents(self):
        list_of_possible_events = ["start", "stop", "restart", "status", "add", "remove", "list"]
        self._logger.debug(f"getting list of possible events: {list_of_possible_events}")
        return list_of_possible_events
        
    async def _getUserPermissionsInStringFor(self, event):
        self._logger.debug(f"_getUserPermissionsInStringFor called. event: {event}")
        user_permissions = self._permissions_manager.getUserPermissionsForEvent(event)
        user_names = await self._getUserNames(user_permissions)
        self._logger.debug(f"_getUserPermissionsInStringFor done. user_names: {user_names}")
        return "\n".join(user_names)
        
    async def _getUserNames(self, user_permissions):
        self._logger.debug(f"_getUserNames called. user_permissions: {user_permissions}")
        tasks = []    
        for user_permission in user_permissions:
            self._logger.debug(f"stringifying user_permission: {user_permission}")
            tasks.append(asyncio.create_task(self._guild.fetch_member(user_permission['id'])))
        self._logger.debug(f"gathering tasks. tasks: {tasks}")
        
        users = await asyncio.gather(*tasks)
        user_names = []
        for user in users:
            user_names.append(user.name)
            
        return user_names
        
    async def _getRolePermissionsInStringFor(self, event):
        self._logger.debug(f"_getRolePermissionsInStringFor called. event: {event}")
        role_permissions = self._permissions_manager.getGroupPermissionsForEvent(event)
        role_names = []
        for role_permission in role_permissions:
            self._logger.debug(f"stringifying role_permission: {role_permission}")
            role_names.append(self._guild.get_role(role_permission['id']).name)
        return "\n".join(role_names)