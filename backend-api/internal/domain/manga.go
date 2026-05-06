package domain

import (
	"time"
)

type MangaMaster struct {
	ID        uint      `gorm:"primaryKey" json:"id"`
	
	TitleTH   string    `gorm:"type:varchar(255);not null" json:"title_th"`
	Publisher string    `gorm:"type:varchar(100)" json:"publisher"`
	VolTH     int       `json:"vol_th"`
	LastUpdTH time.Time `json:"last_update_th"`

	TitleJP   string    `gorm:"type:varchar(255)" json:"title_jp"`
	TitleEN   string    `gorm:"type:varchar(255)" json:"title_en"`
	MalID     int       `gorm:"uniqueIndex" json:"mal_id"`
	VolJP     int       `json:"vol_jp"`
	StatusJP  string    `gorm:"type:varchar(50)" json:"status_jp"`

	//Mapping Status
	IsMapped  bool      `gorm:"default:false" json:"is_mapped"`
	
	CreatedAt time.Time `json:"created_at"`
	UpdatedAt time.Time `json:"updated_at"`
}

type PhoenixManga struct {
	URL         string    `gorm:"primaryKey;type:varchar(255)" json:"url"`
	TitleTH     string    `gorm:"type:varchar(255);not null" json:"title_th"`
	TitleJP        string     `gorm:"type:varchar(255)" json:"title_jp"`
	TitleEN     string    `gorm:"type:varchar(255)" json:"title_en"`
	VolTH       int       `gorm:"type:int" json:"vol_th"`
	VolRaw      string    `gorm:"type:varchar(50)" json:"vol_raw"`
	HasPremium  int       `gorm:"type:int" json:"has_premium"`
	PremiumType string    `gorm:"type:varchar(100)" json:"premium_type"`
	MediaType      string     `gorm:"type:varchar(50);default:'Manga'" json:"media_type"`
	Price          float64    `gorm:"type:decimal(10,2)" json:"price"`
	Authors        []string   `gorm:"type:jsonb;serializer:json" json:"authors"`
	Genres         []string   `gorm:"type:jsonb;serializer:json" json:"genres"`
	JPTotalVols int       `gorm:"type:int;default:0" json:"jp_total_vols"`
	JikanStatus string    `gorm:"type:varchar(50);default:'PENDING'" json:"jikan_status"`
	THReleaseDate  *time.Time `gorm:"type:date" json:"th_release_date"`
	UpdatedAt   time.Time `gorm:"autoUpdateTime" json:"updated_at"`
}

type MangaMLFeature struct {
	TitleTH             string     `gorm:"primaryKey;type:varchar(255)" json:"title_th"`
	TitleEN             string     `gorm:"type:varchar(255)" json:"title_en"`
	LatestReleaseDate   *time.Time `gorm:"type:date" json:"latest_release_date"`
	MaxVolTH            int        `gorm:"type:int" json:"max_vol_th"`
	JPTotalVols         int        `gorm:"type:int" json:"jp_total_vols"`
	TotalPremiumIssues  int        `gorm:"type:int" json:"total_premium_issues"`
	JikanStatus         string     `gorm:"type:varchar(50)" json:"jikan_status"`
	DaysSinceRelease    int        `gorm:"type:int" json:"days_since_release"`
	VolumeGap           int        `gorm:"type:int" json:"volume_gap"`
	AvgReleaseGapDays   float64    `gorm:"type:decimal(10,2)" json:"avg_release_gap_days"`
	DelaySeverityRatio  float64    `gorm:"type:decimal(10,2)" json:"delay_severity_ratio"`
	IsDropped           int        `gorm:"type:int" json:"is_dropped"`
	UpdatedAt           time.Time  `gorm:"autoUpdateTime" json:"updated_at"`
}

