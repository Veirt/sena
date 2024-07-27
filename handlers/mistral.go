package handlers

import (
	"fmt"
	"log"
	"os"

	"github.com/bwmarrin/discordgo"
	"github.com/gage-technologies/mistral-go"
)

var (
	MistralChannelId    = os.Getenv("MISTRAL_CHANNEL_ID")
	mistralApiKey       = os.Getenv("MISTRAL_API_KEY")
	systemPromptContent = os.Getenv("MISTRAL_SYSTEM_PROMPT")
)

type Model struct {
	client  *mistral.MistralClient
	history []mistral.ChatMessage
}

var systemPrompt = mistral.ChatMessage{
	Content: systemPromptContent,
	Role:    mistral.RoleSystem,
}

var model = Model{
	client:  mistral.NewMistralClientDefault(mistralApiKey),
	history: []mistral.ChatMessage{systemPrompt},
}

func HandleMistralMessage(s *discordgo.Session, m *discordgo.MessageCreate) {
	chat := mistral.ChatMessage{
		Content: fmt.Sprintf("(%s): %s", m.Author.Username, m.Content),
		Role:    mistral.RoleUser,
	}
	model.history = append(model.history, chat)

	chatRes, err := model.client.Chat("mistral-large-latest", model.history, nil)
	if err != nil {
		log.Fatalf("Error getting chat completion: %v", err)
		return
	}
	model.history = append(model.history, mistral.ChatMessage{
		Content: chatRes.Choices[0].Message.Content,
		Role:    mistral.RoleAssistant,
	})

	s.ChannelMessageSendReply(m.ChannelID, chatRes.Choices[0].Message.Content, m.Reference())
}
