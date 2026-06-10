package com.secureiot.doorlock_api.model;

import jakarta.persistence.*;

@Entity
@Table(name = "system_settings")
public class SystemSetting {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Integer setting_id;

    @Column(unique = true, nullable = false)
    private String setting_name;

    @Column(nullable = false)
    private String setting_value;

    // Default Constructor
    public SystemSetting() {}

    // Getters and Setters
    public Integer getSetting_id() { return setting_id; }
    public void setSetting_id(Integer setting_id) { this.setting_id = setting_id; }

    public String getSetting_name() { return setting_name; }
    public void setSetting_name(String setting_name) { this.setting_name = setting_name; }

    public String getSetting_value() { return setting_value; }
    public void setSetting_value(String setting_value) { this.setting_value = setting_value; }
}