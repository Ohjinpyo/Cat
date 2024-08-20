package com.example.demo.model;


import jakarta.persistence.*;

@Entity
public class User {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false, unique = true)
    private String username;

    @Column(nullable = false)
    private String password;

    @Column(nullable = false)
    private String apikey;

    @Column(nullable = false)
    private String apisecret;

    @Column(nullable = false)
    private boolean si;

    @Column(nullable = false)
    private boolean aisi;

    @Column(nullable = false)
    private boolean gapsi;

    @Column(nullable = false)
    private boolean at;

    // Getters and setters
    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public String getUsername() {
        return username;
    }

    public void setUsername(String username) {
        this.username = username;
    }

    public String getPassword() {
        return password;
    }

    public void setPassword(String password) {
        this.password = password;
    }

    public String getApikey() {
        return apikey;
    }

    public void setApikey(String apikey) {
        this.apikey = apikey;
    }

    public String getApisecret() {
        return apisecret;
    }

    public void setApisecret(String apisecret) {
        this.apisecret = apisecret;
    }

    public boolean isSi() { return si; }

    public void setSi(boolean si) { this.si = si; }

    public boolean isAisi() { return aisi; }

    public void setAisi(boolean aisi) { this.aisi = aisi; }

    public boolean isGapsi() { return gapsi; }

    public void setGapsi(boolean gapsi) { this.gapsi = gapsi; }

    public boolean isAt() { return at; }

    public void setAt(boolean at) { this.at = at; }
}
