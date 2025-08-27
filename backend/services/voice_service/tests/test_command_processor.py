"""
Voice Command Processor Tests
Tests for voice command recognition and processing
"""
import pytest
from unittest.mock import MagicMock
from datetime import datetime

from services.command_processor import VoiceCommandProcessor, CommandPattern
from core.models import VoiceCommand, CommandType, VoiceResponse
from core.exceptions import VoiceCommandError, UnsupportedCommandError

class TestVoiceCommandProcessor:
    """Test VoiceCommandProcessor class"""
    
    @pytest.fixture
    def command_processor(self):
        """Create VoiceCommandProcessor instance"""
        return VoiceCommandProcessor()
    
    def test_initialization(self, command_processor):
        """Test processor initialization"""
        assert len(command_processor.command_patterns) > 0
        assert "en" in command_processor.command_patterns
        assert "hi" in command_processor.command_patterns
        assert "es" in command_processor.command_patterns
        assert len(command_processor.command_handlers) > 0
    
    @pytest.mark.asyncio
    async def test_parse_command_start_meditation_english(self, command_processor):
        """Test parsing start meditation command in English"""
        command = await command_processor._parse_command(
            "start meditation", 
            "en"
        )
        
        assert command is not None
        assert command.command_type == CommandType.START_MEDITATION
        assert command.language == "en"
        assert command.text == "start meditation"
    
    @pytest.mark.asyncio
    async def test_parse_command_start_meditation_hindi(self, command_processor):
        """Test parsing start meditation command in Hindi"""
        command = await command_processor._parse_command(
            "ध्यान शुरू करो",
            "hi"
        )
        
        assert command is not None
        assert command.command_type == CommandType.START_MEDITATION
        assert command.language == "hi"
    
    @pytest.mark.asyncio
    async def test_parse_command_volume_control_with_parameter(self, command_processor):
        """Test parsing volume control command with parameters"""
        command = await command_processor._parse_command(
            "volume up",
            "en"
        )
        
        assert command is not None
        assert command.command_type == CommandType.VOLUME_CONTROL
        assert "direction" in command.parameters
        assert command.parameters["direction"] == "up"
    
    @pytest.mark.asyncio
    async def test_parse_command_unrecognized(self, command_processor):
        """Test parsing unrecognized command"""
        command = await command_processor._parse_command(
            "xyz unknown command",
            "en"
        )
        
        assert command is None
    
    @pytest.mark.asyncio
    async def test_process_voice_command_success(self, command_processor):
        """Test successful voice command processing"""
        result = await command_processor.process_voice_command(
            text="start meditation",
            language="en",
            user_id="test_user"
        )
        
        assert isinstance(result, VoiceResponse)
        assert result.success is True
        assert "meditation" in result.message.lower()
        assert result.data["action"] == "start_meditation"
    
    @pytest.mark.asyncio
    async def test_process_voice_command_unrecognized(self, command_processor):
        """Test processing unrecognized voice command"""
        result = await command_processor.process_voice_command(
            text="xyz unknown command",
            language="en",
            user_id="test_user"
        )
        
        assert isinstance(result, VoiceResponse)
        assert result.success is False
        assert "not recognized" in result.message
    
    @pytest.mark.asyncio
    async def test_execute_command_start_meditation(self, command_processor):
        """Test executing start meditation command"""
        voice_command = VoiceCommand(
            text="start meditation",
            command_type=CommandType.START_MEDITATION,
            language="en",
            confidence=0.9,
            parameters={},
            context={}
        )
        
        result = await command_processor._execute_command(
            voice_command,
            user_id="test_user"
        )
        
        assert result.success is True
        assert result.data["action"] == "start_meditation"
    
    @pytest.mark.asyncio
    async def test_execute_command_stop_meditation(self, command_processor):
        """Test executing stop meditation command"""
        voice_command = VoiceCommand(
            text="stop meditation",
            command_type=CommandType.STOP_MEDITATION,
            language="en",
            confidence=0.9,
            parameters={},
            context={}
        )
        
        result = await command_processor._execute_command(voice_command)
        
        assert result.success is True
        assert result.data["action"] == "stop_meditation"
    
    @pytest.mark.asyncio
    async def test_execute_command_volume_control(self, command_processor):
        """Test executing volume control command"""
        voice_command = VoiceCommand(
            text="volume up",
            command_type=CommandType.VOLUME_CONTROL,
            language="en",
            confidence=0.9,
            parameters={"direction": "up"},
            context={}
        )
        
        result = await command_processor._execute_command(voice_command)
        
        assert result.success is True
        assert result.data["action"] == "volume_control"
        assert result.data["direction"] == "up"
    
    @pytest.mark.asyncio
    async def test_execute_command_help(self, command_processor):
        """Test executing help command"""
        voice_command = VoiceCommand(
            text="help me",
            command_type=CommandType.HELP,
            language="en",
            confidence=0.9,
            parameters={},
            context={}
        )
        
        result = await command_processor._execute_command(voice_command)
        
        assert result.success is True
        assert result.data["action"] == "help"
        assert "help_text" in result.data
        assert len(result.data["help_text"]) > 0
    
    @pytest.mark.asyncio
    async def test_execute_command_help_hindi(self, command_processor):
        """Test executing help command in Hindi"""
        voice_command = VoiceCommand(
            text="मदद करो",
            command_type=CommandType.HELP,
            language="hi",
            confidence=0.9,
            parameters={},
            context={}
        )
        
        result = await command_processor._execute_command(voice_command)
        
        assert result.success is True
        help_text = result.data["help_text"]
        assert "मैं" in help_text  # Should contain Hindi text
    
    @pytest.mark.asyncio
    async def test_execute_command_unsupported_type(self, command_processor):
        """Test executing unsupported command type"""
        # Remove a handler to test unsupported command
        original_handler = command_processor.command_handlers.pop(CommandType.START_MEDITATION, None)
        
        voice_command = VoiceCommand(
            text="start meditation",
            command_type=CommandType.START_MEDITATION,
            language="en",
            confidence=0.9,
            parameters={},
            context={}
        )
        
        with pytest.raises(UnsupportedCommandError):
            await command_processor._execute_command(voice_command)
        
        # Restore handler
        if original_handler:
            command_processor.command_handlers[CommandType.START_MEDITATION] = original_handler
    
    def test_register_command_handler(self, command_processor):
        """Test registering custom command handler"""
        async def custom_handler(command, user_id, context):
            return VoiceResponse(
                success=True,
                message="Custom command executed",
                data={"action": "custom"}
            )
        
        command_processor.register_command_handler(CommandType.CUSTOM, custom_handler)
        
        assert CommandType.CUSTOM in command_processor.command_handlers
        assert command_processor.command_handlers[CommandType.CUSTOM] == custom_handler
    
    def test_add_command_pattern(self, command_processor):
        """Test adding new command pattern"""
        pattern = CommandPattern(
            pattern="test.*pattern",
            command_type=CommandType.CUSTOM,
            language="en",
            confidence_threshold=0.8
        )
        
        initial_count = len(command_processor.command_patterns["en"])
        command_processor.add_command_pattern(pattern)
        
        assert len(command_processor.command_patterns["en"]) == initial_count + 1
        assert pattern in command_processor.command_patterns["en"]
    
    def test_add_command_pattern_new_language(self, command_processor):
        """Test adding command pattern for new language"""
        pattern = CommandPattern(
            pattern="test.*pattern",
            command_type=CommandType.CUSTOM,
            language="fr",  # New language
            confidence_threshold=0.8
        )
        
        command_processor.add_command_pattern(pattern)
        
        assert "fr" in command_processor.command_patterns
        assert pattern in command_processor.command_patterns["fr"]
    
    def test_get_supported_commands(self, command_processor):
        """Test getting supported commands for a language"""
        commands = command_processor.get_supported_commands("en")
        
        assert isinstance(commands, list)
        assert len(commands) > 0
        
        # Check structure of command info
        command_info = commands[0]
        assert "pattern" in command_info
        assert "command_type" in command_info
        assert "language" in command_info
        assert command_info["language"] == "en"
    
    def test_get_supported_commands_unsupported_language(self, command_processor):
        """Test getting supported commands for unsupported language"""
        commands = command_processor.get_supported_commands("xyz")
        
        assert isinstance(commands, list)
        assert len(commands) == 0
    
    def test_get_command_stats(self, command_processor):
        """Test getting command processing statistics"""
        stats = command_processor.get_command_stats()
        
        assert isinstance(stats, dict)
        assert "uptime_seconds" in stats
        assert "total_commands" in stats
        assert "successful_commands" in stats
        assert "failed_commands" in stats
        assert "success_rate" in stats
        assert "commands_by_type" in stats
        assert "supported_languages" in stats
        assert "total_patterns" in stats
        
        # Verify supported languages
        assert "en" in stats["supported_languages"]
        assert "hi" in stats["supported_languages"]
        assert "es" in stats["supported_languages"]
    
    @pytest.mark.asyncio
    async def test_stats_update_on_success(self, command_processor):
        """Test that stats are updated on successful command processing"""
        initial_stats = command_processor.get_command_stats()
        initial_total = initial_stats["total_commands"]
        initial_successful = initial_stats["successful_commands"]
        
        await command_processor.process_voice_command(
            text="start meditation",
            language="en"
        )
        
        updated_stats = command_processor.get_command_stats()
        assert updated_stats["total_commands"] == initial_total + 1
        assert updated_stats["successful_commands"] == initial_successful + 1
    
    @pytest.mark.asyncio
    async def test_stats_update_on_failure(self, command_processor):
        """Test that stats are updated on failed command processing"""
        initial_stats = command_processor.get_command_stats()
        initial_total = initial_stats["total_commands"]
        initial_failed = initial_stats["failed_commands"]
        
        # Force a failure by making handler raise exception
        original_handler = command_processor.command_handlers[CommandType.START_MEDITATION]
        command_processor.command_handlers[CommandType.START_MEDITATION] = lambda *args: (_ for _ in ()).throw(Exception("Test error"))
        
        try:
            with pytest.raises(VoiceCommandError):
                await command_processor.process_voice_command(
                    text="start meditation",
                    language="en"
                )
        finally:
            # Restore original handler
            command_processor.command_handlers[CommandType.START_MEDITATION] = original_handler
        
        updated_stats = command_processor.get_command_stats()
        assert updated_stats["total_commands"] == initial_total + 1
        assert updated_stats["failed_commands"] == initial_failed + 1
    
    def test_get_help_text_english(self, command_processor):
        """Test getting help text in English"""
        help_text = command_processor._get_help_text("en")
        
        assert isinstance(help_text, str)
        assert len(help_text) > 0
        assert "meditation" in help_text.lower()
        assert "music" in help_text.lower()
    
    def test_get_help_text_hindi(self, command_processor):
        """Test getting help text in Hindi"""
        help_text = command_processor._get_help_text("hi")
        
        assert isinstance(help_text, str)
        assert len(help_text) > 0
        assert "ध्यान" in help_text  # Should contain Hindi text
    
    def test_get_help_text_unsupported_language(self, command_processor):
        """Test getting help text for unsupported language (should fallback to English)"""
        help_text = command_processor._get_help_text("xyz")
        
        assert isinstance(help_text, str)
        assert len(help_text) > 0
        # Should fallback to English
        assert "meditation" in help_text.lower()
    
    @pytest.mark.asyncio
    async def test_meditation_commands_comprehensive(self, command_processor):
        """Test all meditation-related commands"""
        meditation_commands = [
            ("start meditation", CommandType.START_MEDITATION),
            ("stop meditation", CommandType.STOP_MEDITATION),
            ("pause meditation", CommandType.PAUSE_MEDITATION),
            ("resume meditation", CommandType.RESUME_MEDITATION),
            ("guide meditation", CommandType.GUIDED_MEDITATION)
        ]
        
        for text, expected_type in meditation_commands:
            result = await command_processor.process_voice_command(text, "en")
            assert result.success is True
            
            # Parse the command to verify type
            parsed = await command_processor._parse_command(text, "en")
            if parsed:  # Some might not match due to regex patterns
                assert parsed.command_type == expected_type
    
    @pytest.mark.asyncio
    async def test_music_commands_comprehensive(self, command_processor):
        """Test all music-related commands"""
        music_commands = [
            ("play music", CommandType.PLAY_MUSIC),
            ("stop music", CommandType.STOP_MUSIC),
            ("pause music", CommandType.PAUSE_MUSIC),
            ("resume music", CommandType.RESUME_MUSIC)
        ]
        
        for text, expected_type in music_commands:
            result = await command_processor.process_voice_command(text, "en")
            assert result.success is True
            
            parsed = await command_processor._parse_command(text, "en")
            if parsed:
                assert parsed.command_type == expected_type
    
    @pytest.mark.asyncio
    async def test_navigation_commands_comprehensive(self, command_processor):
        """Test all navigation commands"""
        nav_commands = [
            ("go home", CommandType.NAVIGATE_HOME),
            ("open profile", CommandType.NAVIGATE_PROFILE),
            ("open settings", CommandType.NAVIGATE_SETTINGS)
        ]
        
        for text, expected_type in nav_commands:
            result = await command_processor.process_voice_command(text, "en")
            assert result.success is True
            
            parsed = await command_processor._parse_command(text, "en")
            if parsed:
                assert parsed.command_type == expected_type

class TestCommandPattern:
    """Test CommandPattern dataclass"""
    
    def test_command_pattern_creation(self):
        """Test creating command pattern"""
        pattern = CommandPattern(
            pattern="test.*pattern",
            command_type=CommandType.START_MEDITATION,
            language="en",
            confidence_threshold=0.8,
            parameters=["param1"],
            meditation_specific=True
        )
        
        assert pattern.pattern == "test.*pattern"
        assert pattern.command_type == CommandType.START_MEDITATION
        assert pattern.language == "en"
        assert pattern.confidence_threshold == 0.8
        assert pattern.parameters == ["param1"]
        assert pattern.meditation_specific is True
    
    def test_command_pattern_defaults(self):
        """Test command pattern with default values"""
        pattern = CommandPattern(
            pattern="test.*pattern",
            command_type=CommandType.HELP,
            language="en"
        )
        
        assert pattern.confidence_threshold == 0.8  # default
        assert pattern.parameters is None  # default
        assert pattern.meditation_specific is False  # default
