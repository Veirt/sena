package types

import "github.com/bwmarrin/discordgo"

type Command struct {
	Name        string
	Category    string
	Description string
	Run         func(s *discordgo.Session, m *discordgo.MessageCreate)
}
