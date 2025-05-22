package com.veriview.backend.util;

import io.jsonwebtoken.Jwts;
import io.jsonwebtoken.io.Decoders;
import io.jsonwebtoken.security.Keys;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

import jakarta.annotation.PostConstruct;  // 수정: javax에서 jakarta로 변경
import java.security.Key;
import java.util.Date;

@Component
public class JwtTokenProvider {

    @Value("${jwt.secret}")
    private String secretKey;

    private final long validityInMs = 1000 * 60 * 60; // 1 hour
    private Key key;

    @PostConstruct
    public void init() {
        // secretKey가 Base64 인코딩되어 있다고 가정 (아니라면 인코딩 필요)
        byte[] keyBytes = Decoders.BASE64.decode(secretKey);
        this.key = Keys.hmacShaKeyFor(keyBytes);
        
    }

    public String createToken(String userId) {
        Date now = new Date();
        Date expiry = new Date(now.getTime() + validityInMs);

        return Jwts.builder()
                .subject(userId)          // setSubject 대신
                .issuedAt(now)            // setIssuedAt 대신
                .expiration(expiry)       // setExpiration 대신
                .signWith(key)            // SignatureAlgorithm 없이 key만 넘김
                .compact();
    }
}