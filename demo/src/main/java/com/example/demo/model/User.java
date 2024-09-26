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
    private boolean ai2si;

    @Column(nullable = false)
    private boolean ai3si;

    @Column(nullable = false)
    private boolean ai4si;

    @Column(nullable = false)
    private boolean ai5si;

    @Column(nullable = false)
    private boolean ai6si;

    @Column(nullable = false)
    private boolean ai7si;

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

    public boolean isAi2si() {
        return ai2si;
    }

    public void setAi2si(boolean ai2si) {
        this.ai2si = ai2si;
    }

    public boolean isGapsi() { return gapsi; }

    public void setGapsi(boolean gapsi) { this.gapsi = gapsi; }

    public boolean isAt() { return at; }

    public void setAt(boolean at) { this.at = at; }

    public boolean isAi3si() {
        return ai3si;
    }

    public void setAi3si(boolean ai3si) {
        this.ai3si = ai3si;
    }

    public boolean isAi4si() {
        return ai4si;
    }

    public void setAi4si(boolean ai4si) {
        this.ai4si = ai4si;
    }

    public boolean isAi5si() {
        return ai5si;
    }

    public void setAi5si(boolean ai5si) {
        this.ai5si = ai5si;
    }

    public boolean isAi6si() {
        return ai6si;
    }

    public void setAi6si(boolean ai6si) {
        this.ai6si = ai6si;
    }

    public boolean isAi7si() {
        return ai7si;
    }

    public void setAi7si(boolean ai7si) {
        this.ai7si = ai7si;
    }
}
