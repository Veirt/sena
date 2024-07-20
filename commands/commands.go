package commands

import (
	"github.com/veirt/the-fool/types"
)

var cmdMap = make(map[string]types.Command)

func RegisterCommand(cmd types.Command) {
	cmdMap[cmd.Name] = cmd
}

func GetCommands() map[string]types.Command {
	return cmdMap
}
