package com.sentiguard.backend.vo;

import lombok.Data;

@Data
public class FactClaimVO {

    private Long id;

    private String claimText;

    private String claimType;

    private Integer claimOrder;
}
