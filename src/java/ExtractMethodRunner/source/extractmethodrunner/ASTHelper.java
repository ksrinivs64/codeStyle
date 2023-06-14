/*
 * Copyright (c) 2002 - 2006 IBM Corporation.
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *     IBM Corporation - initial API and implementation
 */
package extractmethodrunner;

import java.io.IOException;
import java.util.Hashtable;

import org.eclipse.core.runtime.NullProgressMonitor;
import org.eclipse.jdt.core.JavaCore;
import org.eclipse.jdt.core.compiler.IProblem;
import org.eclipse.jdt.core.dom.AST;
import org.eclipse.jdt.core.dom.ASTParser;
import org.eclipse.jdt.core.dom.FileASTRequestor;

//import com.ibm.wala.properties.WalaProperties;


public class ASTHelper {

//	static String[] stdlibs = WalaProperties.getJ2SEJarFiles();
	

	public static void doASTs(String[] sourceFiles, FileASTRequestor req) throws IOException {
	    @SuppressWarnings("deprecation")
		final ASTParser parser = ASTParser.newParser(AST.JLS8);
	    parser.setResolveBindings(true);
	    parser.setEnvironment(null, new String[0], null, false);
	    Hashtable<String, String> options = JavaCore.getOptions();
	    options.put(JavaCore.COMPILER_SOURCE, "1.8");
	    parser.setCompilerOptions(options);
	    parser.createASTs(
	        sourceFiles, null, new String[0], req, new NullProgressMonitor());
	}

	public static String firstMessageWord(IProblem p) {
		return nthMessageWord(p, 0);
	}
	
	public static String nthMessageWord(IProblem p, int n) {
		return p.getMessage().split("[\\W]+")[n];
	}

	public static String lastMessageWord(IProblem p) {
		String[] words = p.getMessage().split("[\\W]+");
		return words[ words.length-1 ];
	}

	public static boolean hasError(IProblem[] ps) {
		for(IProblem p : ps) {
			if (p.isError()) {
				return true;
			}
		}
		
		return false;
	}
}
