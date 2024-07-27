package commands

import (
	"strings"

	"github.com/veirt/sena/types"
)

var cmdMap = make(map[string]types.Command)

func RegisterCommand(cmd types.Command) {
	cmdMap[cmd.Name] = cmd
}

func GetCommands() map[string]types.Command {
	return cmdMap
}

func GetArguments(text string) string {
	return strings.Join((strings.Split(text, " ")[1:]), " ")
}
