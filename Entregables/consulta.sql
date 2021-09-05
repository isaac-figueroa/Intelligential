SELECT * FROM (
	(
		(SELECT * FROM Pago WHERE id_contrato=@param1 AND fecha<@param2 AND activo=True
		ORDER BY Fecha,id_contrato) AS P
		INNER JOIN Contrato 
		ON P.id_contrato=Contrato.id
	)
	INNER JOIN Cliente
	ON P.id_cliente=Cliente.id
);