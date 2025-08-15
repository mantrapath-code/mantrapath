"""
Voice Command Processor Service
Handles voice command recognition, parsing, and execution
"""
import re
import logging
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime
from dataclasses import dataclass

from core.models import VoiceCommand, VoiceResponse, CommandType
from core.exceptions import VoiceCommandError, UnsupportedCommandError
from config.language_config import SUPPORTED_LANGUAGES

logger = logging.getLogger(__name__)

@dataclass
class CommandPattern:
    """Voice command pattern definition"""
    pattern: str
    command_type: CommandType
    language: str
    confidence_threshold: float = 0.8
    parameters: Optional[List[str]] = None
    meditation_specific: bool = False

class VoiceCommandProcessor:
    """Service for processing and executing voice commands"""
    
    def __init__(self):
        self.command_patterns = self._initialize_command_patterns()
        self.command_handlers: Dict[CommandType, Callable] = {}
        self.execution_stats = {
            "total_commands": 0,
            "successful_commands": 0,
            "failed_commands": 0,
            "commands_by_type": {},
            "start_time": datetime.utcnow()
        }
        self._register_default_handlers()
    
    def _initialize_command_patterns(self) -> Dict[str, List[CommandPattern]]:
        """Initialize command patterns for different languages"""
        
        patterns = {
            "en": [
                # Meditation Commands
                CommandPattern("start.*meditation", CommandType.START_MEDITATION, "en", meditation_specific=True),
                CommandPattern("stop.*meditation", CommandType.STOP_MEDITATION, "en", meditation_specific=True),
                CommandPattern("pause.*meditation", CommandType.PAUSE_MEDITATION, "en", meditation_specific=True),
                CommandPattern("resume.*meditation", CommandType.RESUME_MEDITATION, "en", meditation_specific=True),
                CommandPattern("guide.*meditation", CommandType.GUIDED_MEDITATION, "en", meditation_specific=True),
                
                # Audio Control
                CommandPattern("play.*music", CommandType.PLAY_MUSIC, "en"),
                CommandPattern("stop.*music", CommandType.STOP_MUSIC, "en"),
                CommandPattern("pause.*music", CommandType.PAUSE_MUSIC, "en"),
                CommandPattern("resume.*music", CommandType.RESUME_MUSIC, "en"),
                CommandPattern("next.*track", CommandType.NEXT_TRACK, "en"),
                CommandPattern("previous.*track", CommandType.PREVIOUS_TRACK, "en"),
                CommandPattern("volume.*(up|down|\\d+)", CommandType.VOLUME_CONTROL, "en", parameters=["direction"]),
                
                # Navigation
                CommandPattern("go.*home", CommandType.NAVIGATE_HOME, "en"),
                CommandPattern("open.*profile", CommandType.NAVIGATE_PROFILE, "en"),
                CommandPattern("open.*settings", CommandType.NAVIGATE_SETTINGS, "en"),
                CommandPattern("show.*progress", CommandType.SHOW_PROGRESS, "en"),
                
                # Content Commands
                CommandPattern("search.*for.*", CommandType.SEARCH_CONTENT, "en", parameters=["query"]),
                CommandPattern("bookmark.*this", CommandType.BOOKMARK_CONTENT, "en"),
                CommandPattern("share.*this", CommandType.SHARE_CONTENT, "en"),
                
                # System Commands
                CommandPattern("help.*me", CommandType.HELP, "en"),
                CommandPattern("what.*can.*you.*do", CommandType.HELP, "en"),
                CommandPattern("logout", CommandType.LOGOUT, "en"),
                CommandPattern("quit.*app", CommandType.EXIT_APP, "en"),
            ],
            
            "hi": [
                # Meditation Commands (Hindi)
                CommandPattern("ध्यान.*शुरू.*करो", CommandType.START_MEDITATION, "hi", meditation_specific=True),
                CommandPattern("ध्यान.*बंद.*करो", CommandType.STOP_MEDITATION, "hi", meditation_specific=True),
                CommandPattern("ध्यान.*रोको", CommandType.PAUSE_MEDITATION, "hi", meditation_specific=True),
                CommandPattern("ध्यान.*जारी.*रखो", CommandType.RESUME_MEDITATION, "hi", meditation_specific=True),
                
                # Audio Control (Hindi)
                CommandPattern("संगीत.*चलाओ", CommandType.PLAY_MUSIC, "hi"),
                CommandPattern("संगीत.*बंद.*करो", CommandType.STOP_MUSIC, "hi"),
                CommandPattern("आवाज.*बढ़ाओ", CommandType.VOLUME_CONTROL, "hi", parameters=["up"]),
                CommandPattern("आवाज.*कम.*करो", CommandType.VOLUME_CONTROL, "hi", parameters=["down"]),
                
                # Navigation (Hindi)
                CommandPattern("होम.*जाओ", CommandType.NAVIGATE_HOME, "hi"),
                CommandPattern("प्रोफ़ाइल.*खोलो", CommandType.NAVIGATE_PROFILE, "hi"),
                
                # Help (Hindi)
                CommandPattern("मदद.*करो", CommandType.HELP, "hi"),
                CommandPattern("क्या.*कर.*सकते.*हो", CommandType.HELP, "hi"),
            ],
            
            "es": [
                # Meditation Commands (Spanish)
                CommandPattern("empezar.*meditación", CommandType.START_MEDITATION, "es", meditation_specific=True),
                CommandPattern("parar.*meditación", CommandType.STOP_MEDITATION, "es", meditation_specific=True),
                CommandPattern("pausar.*meditación", CommandType.PAUSE_MEDITATION, "es", meditation_specific=True),
                
                # Audio Control (Spanish)
                CommandPattern("reproducir.*música", CommandType.PLAY_MUSIC, "es"),
                CommandPattern("parar.*música", CommandType.STOP_MUSIC, "es"),
                CommandPattern("subir.*volumen", CommandType.VOLUME_CONTROL, "es", parameters=["up"]),
                CommandPattern("bajar.*volumen", CommandType.VOLUME_CONTROL, "es", parameters=["down"]),
                
                # Help (Spanish)
                CommandPattern("ayúdame", CommandType.HELP, "es"),
                CommandPattern("qué.*puedes.*hacer", CommandType.HELP, "es"),
            ]
        }
        
        return patterns
    
    def _register_default_handlers(self) -> None:
        """Register default command handlers"""
        
        self.command_handlers = {
            CommandType.START_MEDITATION: self._handle_start_meditation,
            CommandType.STOP_MEDITATION: self._handle_stop_meditation,
            CommandType.PAUSE_MEDITATION: self._handle_pause_meditation,
            CommandType.RESUME_MEDITATION: self._handle_resume_meditation,
            CommandType.GUIDED_MEDITATION: self._handle_guided_meditation,
            CommandType.PLAY_MUSIC: self._handle_play_music,
            CommandType.STOP_MUSIC: self._handle_stop_music,
            CommandType.PAUSE_MUSIC: self._handle_pause_music,
            CommandType.RESUME_MUSIC: self._handle_resume_music,
            CommandType.VOLUME_CONTROL: self._handle_volume_control,
            CommandType.NAVIGATE_HOME: self._handle_navigate_home,
            CommandType.NAVIGATE_PROFILE: self._handle_navigate_profile,
            CommandType.NAVIGATE_SETTINGS: self._handle_navigate_settings,
            CommandType.SEARCH_CONTENT: self._handle_search_content,
            CommandType.BOOKMARK_CONTENT: self._handle_bookmark_content,
            CommandType.HELP: self._handle_help,
            CommandType.LOGOUT: self._handle_logout,
            CommandType.CUSTOM: self._handle_custom_command
        }
    
    async def process_voice_command(
        self,
        text: str,
        language: str = "en",
        user_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> VoiceResponse:
        """Process voice command from transcribed text"""
        
        try:
            self.execution_stats["total_commands"] += 1
            
            # Parse command from text
            voice_command = await self._parse_command(text, language, context)
            
            if not voice_command:
                return VoiceResponse(
                    success=False,
                    message=f"Command not recognized: '{text}'",
                    data={"original_text": text, "language": language}
                )
            
            # Execute command
            result = await self._execute_command(voice_command, user_id, context)
            
            # Update stats
            self.execution_stats["successful_commands"] += 1
            command_type_str = voice_command.command_type.value
            self.execution_stats["commands_by_type"][command_type_str] = (
                self.execution_stats["commands_by_type"].get(command_type_str, 0) + 1
            )
            
            return result
            
        except Exception as e:
            self.execution_stats["failed_commands"] += 1
            logger.error(f"Command processing failed: {e}")
            
            if isinstance(e, VoiceCommandError):
                raise e
            else:
                raise VoiceCommandError(f"Command processing failed: {str(e)}")
    
    async def _parse_command(
        self,
        text: str,
        language: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Optional[VoiceCommand]:
        """Parse voice command from text using pattern matching"""
        
        # Normalize text for better pattern matching
        normalized_text = text.lower().strip()
        
        # Get patterns for the language
        patterns = self.command_patterns.get(language, [])
        
        # Try to match patterns
        for pattern in patterns:
            match = re.search(pattern.pattern, normalized_text, re.IGNORECASE)
            if match:
                # Extract parameters if defined
                parameters = {}
                if pattern.parameters:
                    groups = match.groups()
                    for i, param_name in enumerate(pattern.parameters):
                        if i < len(groups) and groups[i]:
                            parameters[param_name] = groups[i]
                
                return VoiceCommand(
                    text=text,
                    command_type=pattern.command_type,
                    language=language,
                    confidence=pattern.confidence_threshold,
                    user_context=parameters,
                    context=context or {}
                )
        
        return None
    
    async def _execute_command(
        self,
        command: VoiceCommand,
        user_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> VoiceResponse:
        """Execute a parsed voice command"""
        
        handler = self.command_handlers.get(command.command_type)
        if not handler:
            raise UnsupportedCommandError(f"No handler for command type: {command.command_type}")
        
        try:
            return await handler(command, user_id, context)
        except Exception as e:
            logger.error(f"Command handler failed for {command.command_type}: {e}")
            raise VoiceCommandError(f"Command execution failed: {str(e)}")
    
    # Default Command Handlers
    
    async def _handle_start_meditation(
        self,
        command: VoiceCommand,
        user_id: Optional[str],
        context: Optional[Dict[str, Any]]
    ) -> VoiceResponse:
        """Handle start meditation command"""
        
        return VoiceResponse(
            success=True,
            message="Starting meditation session",
            data={
                "action": "start_meditation",
                "command": command.dict(),
                "next_steps": "Redirecting to meditation player"
            }
        )
    
    async def _handle_stop_meditation(
        self,
        command: VoiceCommand,
        user_id: Optional[str],
        context: Optional[Dict[str, Any]]
    ) -> VoiceResponse:
        """Handle stop meditation command"""
        
        return VoiceResponse(
            success=True,
            message="Stopping meditation session",
            data={
                "action": "stop_meditation",
                "command": command.dict()
            }
        )
    
    async def _handle_pause_meditation(
        self,
        command: VoiceCommand,
        user_id: Optional[str],
        context: Optional[Dict[str, Any]]
    ) -> VoiceResponse:
        """Handle pause meditation command"""
        
        return VoiceResponse(
            success=True,
            message="Pausing meditation session",
            data={
                "action": "pause_meditation",
                "command": command.dict()
            }
        )
    
    async def _handle_resume_meditation(
        self,
        command: VoiceCommand,
        user_id: Optional[str],
        context: Optional[Dict[str, Any]]
    ) -> VoiceResponse:
        """Handle resume meditation command"""
        
        return VoiceResponse(
            success=True,
            message="Resuming meditation session",
            data={
                "action": "resume_meditation",
                "command": command.dict()
            }
        )
    
    async def _handle_guided_meditation(
        self,
        command: VoiceCommand,
        user_id: Optional[str],
        context: Optional[Dict[str, Any]]
    ) -> VoiceResponse:
        """Handle guided meditation command"""
        
        return VoiceResponse(
            success=True,
            message="Starting guided meditation",
            data={
                "action": "guided_meditation",
                "command": command.dict(),
                "next_steps": "Redirecting to guided meditation selection"
            }
        )
    
    async def _handle_play_music(
        self,
        command: VoiceCommand,
        user_id: Optional[str],
        context: Optional[Dict[str, Any]]
    ) -> VoiceResponse:
        """Handle play music command"""
        
        return VoiceResponse(
            success=True,
            message="Starting music playback",
            data={
                "action": "play_music",
                "command": command.dict()
            }
        )
    
    async def _handle_stop_music(
        self,
        command: VoiceCommand,
        user_id: Optional[str],
        context: Optional[Dict[str, Any]]
    ) -> VoiceResponse:
        """Handle stop music command"""
        
        return VoiceResponse(
            success=True,
            message="Stopping music playback",
            data={
                "action": "stop_music",
                "command": command.dict()
            }
        )
    
    async def _handle_pause_music(
        self,
        command: VoiceCommand,
        user_id: Optional[str],
        context: Optional[Dict[str, Any]]
    ) -> VoiceResponse:
        """Handle pause music command"""
        
        return VoiceResponse(
            success=True,
            message="Pausing music playback",
            data={
                "action": "pause_music",
                "command": command.dict()
            }
        )
    
    async def _handle_resume_music(
        self,
        command: VoiceCommand,
        user_id: Optional[str],
        context: Optional[Dict[str, Any]]
    ) -> VoiceResponse:
        """Handle resume music command"""
        
        return VoiceResponse(
            success=True,
            message="Resuming music playback",
            data={
                "action": "resume_music",
                "command": command.dict()
            }
        )
    
    async def _handle_volume_control(
        self,
        command: VoiceCommand,
        user_id: Optional[str],
        context: Optional[Dict[str, Any]]
    ) -> VoiceResponse:
        """Handle volume control command"""
        
        direction = command.parameters.get("direction", "up")
        
        return VoiceResponse(
            success=True,
            message=f"Adjusting volume {direction}",
            data={
                "action": "volume_control",
                "direction": direction,
                "command": command.dict()
            }
        )
    
    async def _handle_navigate_home(
        self,
        command: VoiceCommand,
        user_id: Optional[str],
        context: Optional[Dict[str, Any]]
    ) -> VoiceResponse:
        """Handle navigate home command"""
        
        return VoiceResponse(
            success=True,
            message="Navigating to home screen",
            data={
                "action": "navigate",
                "destination": "home",
                "command": command.dict()
            }
        )
    
    async def _handle_navigate_profile(
        self,
        command: VoiceCommand,
        user_id: Optional[str],
        context: Optional[Dict[str, Any]]
    ) -> VoiceResponse:
        """Handle navigate profile command"""
        
        return VoiceResponse(
            success=True,
            message="Opening user profile",
            data={
                "action": "navigate",
                "destination": "profile",
                "command": command.dict()
            }
        )
    
    async def _handle_navigate_settings(
        self,
        command: VoiceCommand,
        user_id: Optional[str],
        context: Optional[Dict[str, Any]]
    ) -> VoiceResponse:
        """Handle navigate settings command"""
        
        return VoiceResponse(
            success=True,
            message="Opening settings",
            data={
                "action": "navigate",
                "destination": "settings",
                "command": command.dict()
            }
        )
    
    async def _handle_search_content(
        self,
        command: VoiceCommand,
        user_id: Optional[str],
        context: Optional[Dict[str, Any]]
    ) -> VoiceResponse:
        """Handle search content command"""
        
        query = command.parameters.get("query", "")
        
        return VoiceResponse(
            success=True,
            message=f"Searching for: {query}",
            data={
                "action": "search",
                "query": query,
                "command": command.dict()
            }
        )
    
    async def _handle_bookmark_content(
        self,
        command: VoiceCommand,
        user_id: Optional[str],
        context: Optional[Dict[str, Any]]
    ) -> VoiceResponse:
        """Handle bookmark content command"""
        
        return VoiceResponse(
            success=True,
            message="Bookmarking current content",
            data={
                "action": "bookmark",
                "command": command.dict()
            }
        )
    
    async def _handle_help(
        self,
        command: VoiceCommand,
        user_id: Optional[str],
        context: Optional[Dict[str, Any]]
    ) -> VoiceResponse:
        """Handle help command"""
        
        help_text = self._get_help_text(command.language)
        
        return VoiceResponse(
            success=True,
            message="Here's what I can help you with",
            data={
                "action": "help",
                "help_text": help_text,
                "command": command.dict()
            }
        )
    
    async def _handle_logout(
        self,
        command: VoiceCommand,
        user_id: Optional[str],
        context: Optional[Dict[str, Any]]
    ) -> VoiceResponse:
        """Handle logout command"""
        
        return VoiceResponse(
            success=True,
            message="Logging out",
            data={
                "action": "logout",
                "command": command.dict()
            }
        )
    
    async def _handle_custom_command(
        self,
        command: VoiceCommand,
        user_id: Optional[str],
        context: Optional[Dict[str, Any]]
    ) -> VoiceResponse:
        """Handle custom command"""
        
        return VoiceResponse(
            success=True,
            message="Processing custom command",
            data={
                "action": "custom",
                "command": command.dict()
            }
        )
    
    def _get_help_text(self, language: str = "en") -> str:
        """Get help text for the specified language"""
        
        help_texts = {
            "en": """
I can help you with:
• Meditation: "start meditation", "stop meditation", "pause meditation"
• Music: "play music", "stop music", "volume up/down"
• Navigation: "go home", "open profile", "open settings"
• Content: "search for...", "bookmark this"
• General: "help me", "logout"
            """.strip(),
            
            "hi": """
मैं आपकी मदद कर सकता हूं:
• ध्यान: "ध्यान शुरू करो", "ध्यान बंद करो", "ध्यान रोको"
• संगीत: "संगीत चलाओ", "संगीत बंद करो", "आवाज बढ़ाओ/कम करो"
• नेविगेशन: "होम जाओ", "प्रोफ़ाइल खोलो"
• सहायता: "मदद करो"
            """.strip(),
            
            "es": """
Puedo ayudarte con:
• Meditación: "empezar meditación", "parar meditación", "pausar meditación"
• Música: "reproducir música", "parar música", "subir/bajar volumen"
• Navegación: "ir a inicio", "abrir perfil"
• Ayuda: "ayúdame"
            """.strip()
        }
        
        return help_texts.get(language, help_texts["en"])
    
    def register_command_handler(
        self,
        command_type: CommandType,
        handler: Callable
    ) -> None:
        """Register a custom command handler"""
        
        self.command_handlers[command_type] = handler
        logger.info(f"Registered custom handler for {command_type}")
    
    def add_command_pattern(
        self,
        pattern: CommandPattern
    ) -> None:
        """Add a new command pattern"""
        
        if pattern.language not in self.command_patterns:
            self.command_patterns[pattern.language] = []
        
        self.command_patterns[pattern.language].append(pattern)
        logger.info(f"Added command pattern for {pattern.command_type} in {pattern.language}")
    
    def get_supported_commands(self, language: str = "en") -> List[Dict[str, Any]]:
        """Get list of supported commands for a language"""
        
        patterns = self.command_patterns.get(language, [])
        
        return [
            {
                "pattern": pattern.pattern,
                "command_type": pattern.command_type.value,
                "language": pattern.language,
                "meditation_specific": pattern.meditation_specific,
                "parameters": pattern.parameters or []
            }
            for pattern in patterns
        ]
    
    def get_command_stats(self) -> Dict[str, Any]:
        """Get command processing statistics"""
        
        uptime = datetime.utcnow() - self.execution_stats["start_time"]
        
        return {
            "uptime_seconds": uptime.total_seconds(),
            "total_commands": self.execution_stats["total_commands"],
            "successful_commands": self.execution_stats["successful_commands"],
            "failed_commands": self.execution_stats["failed_commands"],
            "success_rate": (
                self.execution_stats["successful_commands"] / 
                max(1, self.execution_stats["total_commands"])
            ),
            "commands_by_type": self.execution_stats["commands_by_type"],
            "supported_languages": list(self.command_patterns.keys()),
            "total_patterns": sum(len(patterns) for patterns in self.command_patterns.values())
        }
