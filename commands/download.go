package commands

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"log"
	"mime/multipart"
	"net/http"
	"os"
	"strings"

	"github.com/bwmarrin/discordgo"
	"github.com/veirt/the-fool/types"
)

type QBittorrent struct {
	client *http.Client
	host   string
}

type QBCategory struct {
	Name     string `json:"name"`
	SavePath string `json:"savePath"`
}

var conn = QBittorrent{
	client: &http.Client{},
	host:   os.Getenv("QBITTORRENT_HOST"),
}

func (q *QBittorrent) getCategories() (map[string]bool, error) {
	endpoint := "/api/v2/torrents/categories"

	data := map[string]QBCategory{}

	req, err := http.NewRequest("GET", q.host+endpoint, nil)
	if err != nil {
		return nil, fmt.Errorf("error creating request: %w", err)
	}

	res, err := q.client.Do(req)
	if err != nil {
		return nil, fmt.Errorf("error making request: %w", err)
	}
	defer res.Body.Close()

	err = json.NewDecoder(res.Body).Decode(&data)
	if err != nil {
		return nil, fmt.Errorf("error decoding JSON: %w", err)
	}

	categories := map[string]bool{}
	for _, category := range data {
		categories[category.Name] = true
	}

	return categories, nil
}

func (q *QBittorrent) checkCategory(torrents map[string]string) error {
	categories, err := conn.getCategories()
	if err != nil {
		return fmt.Errorf("error fetching categories: %w", err)
	}

	for _, name := range torrents {
		if name == "" || categories[name] {
			continue
		}

		return fmt.Errorf("category '%s' doesn't exist.", name)
	}

	return nil
}

func (q *QBittorrent) isValidTorrentURI(uri string) bool {
	if strings.HasPrefix(uri, "magnet:?xt=urn:btih:") {
		return true
	}

	if (strings.HasPrefix(uri, "http://") || strings.HasPrefix(uri, "https://")) && strings.Contains(uri, ".torrent") {
		return true
	}

	return false
}

func (q *QBittorrent) download(torrent string, category string) error {
	endpoint := "/api/v2/torrents/add"

	var b bytes.Buffer
	w := multipart.NewWriter(&b)
	w.WriteField("urls", torrent)
	w.WriteField("category", category)
	w.Close()

	req, err := http.NewRequest("POST", q.host+endpoint, &b)
	if err != nil {
		return fmt.Errorf("error creating download request: %w", err)
	}
	req.Header.Set("Content-Type", w.FormDataContentType())

	res, err := q.client.Do(req)
	if err != nil {
		return fmt.Errorf("error making download request: %w", err)
	}
	defer res.Body.Close()

	if res.StatusCode != http.StatusOK {
		body, _ := io.ReadAll(res.Body)
		return fmt.Errorf("download request failed: %s", string(body))
	}

	log.Println("Download request successful:", torrent)

	return nil

}

var download = types.Command{
	Name:        "download",
	Category:    "utility",
	Description: "Download to qBittorrent/Ariang instance",
	Run: func(s *discordgo.Session, m *discordgo.MessageCreate) {
		// key: uri, value: category
		torrents := map[string]string{}

		arg := GetArguments(m.Content)
		splitted := strings.Split(arg, "\n")
		for _, arg := range splitted {
			// [uri] [category]
			parts := strings.SplitN(arg, " ", 2)

			uri := parts[0]
			category := ""
			if len(parts) == 2 {
				torrents[uri] = parts[1]
				category = parts[1]
			}

			torrents[uri] = category
		}

		// validate torrent uri
		for uri := range torrents {
			if !conn.isValidTorrentURI(uri) {
				s.ChannelMessageSendReply(m.ChannelID, fmt.Sprintf("'%s' is not a valid torrent URI", uri), m.Reference())
				return
			}
		}

		// validate torrent category
		if err := conn.checkCategory(torrents); err != nil {
			s.ChannelMessageSendReply(m.ChannelID, fmt.Sprintf("Error: %s", err), m.Reference())
			return
		}

		s.ChannelMessageSendReply(m.ChannelID, fmt.Sprintf("Downloading %d torrent(s)", len(torrents)), m.Reference())
		for uri, category := range torrents {
			err := conn.download(uri, category)
			if err != nil {
				s.ChannelMessageSendReply(m.ChannelID, fmt.Sprintf("Error when downloading '%s'\n%s", uri, err), m.Reference())
			}
		}
	},
}

func init() {
	RegisterCommand(download)
}
